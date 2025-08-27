import requests
import json
import re
import os
from typing import List, Dict, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMLogAnomalyDetector:
    """LLM tabanlı log anomali tespit sistemi - Ollama kullanır"""
    
    def __init__(self):
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model_name = "llama3.2"
        self.is_ready = False
        self.is_trained = True  # LLM için her zaman True (eğitim gerektirmez)
        
        # Ollama'nın çalışıp çalışmadığını kontrol et
        self.check_ollama_status()
    
    def check_ollama_status(self):
        """Ollama servisinin çalışıp çalışmadığını kontrol et"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                
                if any(self.model_name in name for name in model_names):
                    self.is_ready = True
                    logger.info(f"Ollama hazır - {self.model_name} modeli mevcut")
                else:
                    logger.warning(f"Ollama çalışıyor ama {self.model_name} modeli yok")
                    self.pull_model()
            else:
                logger.warning("Ollama çalışmıyor veya erişilemiyor")
        except Exception as e:
            logger.error(f"Ollama bağlantı hatası: {str(e)}")
            logger.info("Ollama kurulumu için: https://ollama.ai/download")
    
    def pull_model(self):
        """Gerekli modeli indir"""
        try:
            logger.info(f"{self.model_name} modeli indiriliyor...")
            response = requests.post(
                f"{self.ollama_url}/api/pull",
                json={"name": self.model_name},
                timeout=300  # 5 dakika timeout
            )
            if response.status_code == 200:
                self.is_ready = True
                logger.info(f"{self.model_name} modeli başarıyla indirildi")
            else:
                logger.error(f"Model indirme hatası: {response.text}")
        except Exception as e:
            logger.error(f"Model indirme hatası: {str(e)}")
    
    def create_analysis_prompt(self, log_lines: List[str]) -> str:
        """Log analizi için prompt oluştur"""
        # İlk 10 satırı al (çok uzun olmasın)
        sample_lines = log_lines[:10] if len(log_lines) > 10 else log_lines
        
        prompt = f"""Log analiz uzmanı olarak aşağıdaki log satırlarını analiz et. Sadece JSON formatında yanıt ver:

Log Satırları:
{chr(10).join(f"{i+1}: {line}" for i, line in enumerate(sample_lines))}

Yanıt formatı:
{{
  "results": [
    {{
      "line_number": 1,
      "is_anomaly": true,
      "severity": "critical",
      "anomaly_type": "sistem_hatası",
      "confidence": 0.95,
      "explanation": "ERROR kelimesi tespit edildi"
    }}
  ],
  "summary": {{
    "total_lines": {len(sample_lines)},
    "anomaly_count": 1,
    "critical_count": 1
  }}
}}

Anomali kriterleri: ERROR, CRITICAL, FAIL, EXCEPTION kelimelerini ara."""

        return prompt
    
    def call_ollama(self, prompt: str) -> Dict:
        """Ollama API çağrısı yap"""
        try:
            if not self.is_ready:
                return {"status": "error", "message": "Ollama hazır değil"}
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Daha tutarlı sonuçlar için
                    "top_p": 0.9,
                    "num_predict": 2000  # Maksimum token sayısı
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=60  # Büyük dosyalar için timeout artırıldı
            )
            
            if response.status_code == 200:
                result = response.json()
                return {"status": "success", "response": result.get("response", "")}
            else:
                return {"status": "error", "message": f"API hatası: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Ollama API çağrısı hatası: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def parse_llm_response(self, response_text: str) -> Dict:
        """LLM yanıtını parse et"""
        try:
            # JSON'u bulmaya çalış
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                parsed = json.loads(json_str)
                return parsed
            else:
                # JSON bulunamazsa basit parsing yap
                return self.fallback_parsing(response_text)
                
        except json.JSONDecodeError:
            logger.warning("JSON parse edilemedi, fallback parsing kullanılıyor")
            return self.fallback_parsing(response_text)
    
    def smart_sample_logs(self, log_lines: List[str], target_size: int = 300) -> List[str]:
        """Akıllı log sampling - önemli logları koruyarak dosya boyutunu küçültür"""
        if len(log_lines) <= target_size:
            return log_lines
        
        # Öncelikli keywords (anomali olma ihtimali yüksek)
        priority_keywords = ['ERROR', 'CRITICAL', 'FATAL', 'EXCEPTION', 'FAIL', 'TIMEOUT', 'CRASH']
        warning_keywords = ['WARNING', 'WARN', 'ALERT']
        
        # Logları kategorize et
        priority_logs = []
        warning_logs = []
        normal_logs = []
        
        for i, line in enumerate(log_lines):
            line_upper = line.upper()
            if any(keyword in line_upper for keyword in priority_keywords):
                priority_logs.append((i, line))
            elif any(keyword in line_upper for keyword in warning_keywords):
                warning_logs.append((i, line))
            else:
                normal_logs.append((i, line))
        
        # Sampling stratejisi
        selected_logs = []
        
        # 1. Tüm priority logları al (max 100)
        selected_logs.extend(priority_logs[:100])
        remaining = target_size - len(selected_logs)
        
        # 2. Warning loglarından yarısını al
        if remaining > 0 and warning_logs:
            warning_sample = min(remaining // 2, len(warning_logs))
            selected_logs.extend(warning_logs[:warning_sample])
            remaining -= warning_sample
        
        # 3. Normal loglardan eşit aralıklarla sample al
        if remaining > 0 and normal_logs:
            step = max(1, len(normal_logs) // remaining)
            for i in range(0, len(normal_logs), step):
                if len(selected_logs) >= target_size:
                    break
                selected_logs.append(normal_logs[i])
        
        # Orijinal sıralamayı koru
        selected_logs.sort(key=lambda x: x[0])
        
        # Sadece log metinlerini döndür
        return [log for _, log in selected_logs]

    def fallback_parsing(self, text: str) -> Dict:
        """JSON parse edilemezse basit text parsing"""
        lines = text.split('\n')
        anomaly_count = 0
        critical_count = 0
        
        # Basit keyword arama
        for line in lines:
            if any(word in line.lower() for word in ['error', 'critical', 'fail', 'exception']):
                anomaly_count += 1
                if 'critical' in line.lower():
                    critical_count += 1
            
            return {
            "results": [
                {
                    "line_number": 1,
                    "is_anomaly": anomaly_count > 0,
                    "severity": "critical" if critical_count > 0 else "warning" if anomaly_count > 0 else "normal",
                    "anomaly_type": "sistem_hatası",
                    "confidence": 0.7,
                    "explanation": f"{anomaly_count} potansiyel anomali tespit edildi"
                }
            ],
            "summary": {
                "total_lines": 1,
                "anomaly_count": anomaly_count,
                "critical_count": critical_count
            }
        }
    
    def predict(self, log_lines: List[str]) -> Dict:
        """Log satırları için anomali tahmini yap"""
        try:
            if not log_lines:
                return {"status": "error", "message": "Log satırları boş"}
            
            logger.info(f"LLM ile anomali analizi başlıyor... {len(log_lines)} satır")
            
            # Büyük dosyalar için akıllı sampling
            if len(log_lines) > 500:
                logger.info(f"Büyük dosya ({len(log_lines)} satır), akıllı sampling uygulanıyor")
                log_lines = self.smart_sample_logs(log_lines, target_size=300)
                logger.info(f"Sampling sonrası: {len(log_lines)} satır")
            
            # Batch işleme (küçük batch size)
            batch_size = 20
            all_results = []
            total_anomalies = 0
            total_critical = 0
            
            total_batches = (len(log_lines) + batch_size - 1) // batch_size
            
            for batch_idx, i in enumerate(range(0, len(log_lines), batch_size)):
                batch = log_lines[i:i + batch_size]
                progress = ((batch_idx + 1) / total_batches) * 100
                
                logger.info(f"Batch {batch_idx + 1}/{total_batches} işleniyor... ({progress:.1f}%)")
                
                # Prompt oluştur
                prompt = self.create_analysis_prompt(batch)
                
                # LLM çağrısı
                llm_response = self.call_ollama(prompt)
                
                if llm_response["status"] == "error":
                    logger.error(f"Batch {batch_idx + 1} LLM hatası: {llm_response['message']}")
                    continue
                
                # Yanıtı parse et
                parsed_result = self.parse_llm_response(llm_response["response"])
                
                # Batch sonuçlarını ekle
                if "results" in parsed_result:
                    for result in parsed_result["results"]:
                        # Line number'ları düzelt
                        result["line_number"] = i + result["line_number"]
                        result["log_content"] = batch[result["line_number"] - i - 1] if result["line_number"] - i - 1 < len(batch) else ""
                        
                        if result.get("is_anomaly", False):
                            total_anomalies += 1
                            if result.get("severity") == "critical":
                                total_critical += 1
                        
                        all_results.append(result)
            
            # Kapsamlı rapor oluştur
            report = self.generate_security_report(all_results, log_lines)
            
            return {
                "status": "success",
                "total_lines": len(log_lines),
                "anomaly_count": total_anomalies,
                "critical_count": total_critical,
                "anomaly_rate": total_anomalies / len(log_lines) if len(log_lines) > 0 else 0,
                "results": all_results,
                "security_report": report
            }
            
        except Exception as e:
            logger.error(f"LLM prediction hatası: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def train_model(self, log_lines: List[str], labels: Optional[List[int]] = None):
        """LLM için eğitim gerekmiyor, sadece uyumluluk için"""
        logger.info("LLM tabanlı sistem için model eğitimi gerekmiyor")
        return {
            "status": "success",
            "message": "LLM hazır, eğitim gerekmiyor",
            "training_samples": len(log_lines) if log_lines else 0
        }
    
    def save_model(self):
        """LLM için model kaydetme gerekmiyor"""
        return True
    
    def load_model(self) -> bool:
        """LLM hazır mı kontrol et"""
        return self.is_ready
    
    def generate_security_report(self, analysis_results: List[Dict], log_lines: List[str]) -> Dict:
        """Kapsamlı güvenlik analiz raporu oluştur"""
        from datetime import datetime
        
        # Anomali türlerini kategorize et
        attack_categories = {
            "authentication": ["login", "auth", "password", "token", "credential"],
            "network": ["connection", "timeout", "network", "dns", "port"],
            "system": ["memory", "disk", "cpu", "process", "service"],
            "database": ["sql", "database", "query", "connection"],
            "access_control": ["permission", "denied", "unauthorized", "forbidden"],
            "data_breach": ["breach", "leak", "exposure", "sensitive"],
            "malware": ["virus", "malware", "trojan", "suspicious"],
            "dos_attacks": ["flood", "overload", "exhausted", "limit"]
        }
        
        # Anomalileri kategorize et
        categorized_anomalies = {category: [] for category in attack_categories}
        severity_count = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for result in analysis_results:
            if result.get("is_anomaly"):
                message = result.get("log_content", "").lower()
                explanation = result.get("explanation", "").lower()
                severity = result.get("severity", "medium")
                
                # Severity sayısını artır
                if severity in severity_count:
                    severity_count[severity] += 1
                
                # Kategorilere ayır
                categorized = False
                for category, keywords in attack_categories.items():
                    if any(keyword in message or keyword in explanation for keyword in keywords):
                        categorized_anomalies[category].append(result)
                        categorized = True
                        break
                
                if not categorized:
                    if "other" not in categorized_anomalies:
                        categorized_anomalies["other"] = []
                    categorized_anomalies["other"].append(result)
        
        # Risk skoru hesapla
        total_anomalies = len([r for r in analysis_results if r.get("is_anomaly")])
        risk_score = self.calculate_risk_score(severity_count, total_anomalies, len(log_lines))
        
        # Öneriler oluştur
        recommendations = self.generate_recommendations(categorized_anomalies, severity_count)
        
        # Siber saldırı tespitleri
        potential_attacks = self.identify_potential_attacks(categorized_anomalies)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_logs": len(log_lines),
                "total_anomalies": total_anomalies,
                "risk_score": risk_score,
                "risk_level": self.get_risk_level(risk_score),
                "severity_distribution": severity_count
            },
            "attack_categories": {k: len(v) for k, v in categorized_anomalies.items() if v},
            "potential_attacks": potential_attacks,
            "detailed_findings": categorized_anomalies,
            "recommendations": recommendations,
            "analysis_methodology": {
                "ai_model": "Llama 3.2",
                "analysis_criteria": [
                    "ERROR ve CRITICAL log seviyeleri",
                    "Kimlik doğrulama hataları",
                    "Ağ bağlantı sorunları",
                    "Sistem kaynak tükenmesi",
                    "Erişim kontrolü ihlalleri",
                    "Anormal sistem davranışları"
                ],
                "detection_patterns": [
                    "Başarısız login denemeleri",
                    "Yetkisiz erişim girişimleri",
                    "Sistem kaynak anomalileri",
                    "Ağ trafiği anomalileri",
                    "Veri bütünlüğü sorunları"
                ]
            }
        }
        
        return report
    
    def calculate_risk_score(self, severity_count: Dict, total_anomalies: int, total_logs: int) -> float:
        """Risk skoru hesapla (0-100 arası)"""
        if total_logs == 0:
            return 0
        
        # Ağırlıklı risk hesaplama
        weighted_score = (
            severity_count.get("critical", 0) * 10 +
            severity_count.get("high", 0) * 7 +
            severity_count.get("medium", 0) * 4 +
            severity_count.get("low", 0) * 1
        )
        
        # Anomali oranını dikkate al
        anomaly_rate = total_anomalies / total_logs
        base_score = (weighted_score / total_logs) * 100
        
        # Anomali yoğunluğu faktörü
        density_factor = min(anomaly_rate * 2, 1.5)
        
        final_score = min(base_score * density_factor, 100)
        return round(final_score, 2)
    
    def get_risk_level(self, risk_score: float) -> str:
        """Risk seviyesi belirle"""
        if risk_score >= 80:
            return "CRITICAL"
        elif risk_score >= 60:
            return "HIGH"
        elif risk_score >= 40:
            return "MEDIUM"
        elif risk_score >= 20:
            return "LOW"
        else:
            return "MINIMAL"
    
    def identify_potential_attacks(self, categorized_anomalies: Dict) -> List[Dict]:
        """Potansiyel siber saldırıları tespit et"""
        attacks = []
        
        # Brute Force Attack
        auth_anomalies = len(categorized_anomalies.get("authentication", []))
        if auth_anomalies >= 3:
            attacks.append({
                "attack_type": "Brute Force Attack",
                "description": "Çoklu başarısız kimlik doğrulama denemeleri tespit edildi",
                "severity": "HIGH",
                "indicators": f"{auth_anomalies} kimlik doğrulama anomalisi",
                "recommendation": "IP bazlı rate limiting ve account lockout politikaları uygulayın"
            })
        
        # DDoS/DoS Attack
        network_anomalies = len(categorized_anomalies.get("network", []))
        dos_anomalies = len(categorized_anomalies.get("dos_attacks", []))
        if network_anomalies >= 5 or dos_anomalies >= 2:
            attacks.append({
                "attack_type": "DDoS/DoS Attack",
                "description": "Ağ trafiği anomalileri ve servis kesintileri tespit edildi",
                "severity": "CRITICAL",
                "indicators": f"{network_anomalies} ağ anomalisi, {dos_anomalies} DoS göstergesi",
                "recommendation": "DDoS koruması ve trafik filtreleme sistemleri devreye alın"
            })
        
        # Privilege Escalation
        access_anomalies = len(categorized_anomalies.get("access_control", []))
        if access_anomalies >= 2:
            attacks.append({
                "attack_type": "Privilege Escalation",
                "description": "Yetkisiz erişim denemeleri ve yetki yükseltme girişimleri",
                "severity": "HIGH",
                "indicators": f"{access_anomalies} erişim kontrolü ihlali",
                "recommendation": "Kullanıcı yetkilerini gözden geçirin ve principle of least privilege uygulayın"
            })
        
        # System Compromise
        system_anomalies = len(categorized_anomalies.get("system", []))
        malware_anomalies = len(categorized_anomalies.get("malware", []))
        if system_anomalies >= 4 or malware_anomalies >= 1:
            attacks.append({
                "attack_type": "System Compromise",
                "description": "Sistem bütünlüğü ihlalleri ve şüpheli aktiviteler",
                "severity": "CRITICAL",
                "indicators": f"{system_anomalies} sistem anomalisi, {malware_anomalies} malware göstergesi",
                "recommendation": "Acil sistem taraması yapın ve etkilenen sistemleri izole edin"
            })
        
        # SQL Injection
        db_anomalies = len(categorized_anomalies.get("database", []))
        if db_anomalies >= 2:
            attacks.append({
                "attack_type": "SQL Injection",
                "description": "Veritabanı erişim anomalileri ve şüpheli sorgular",
                "severity": "HIGH",
                "indicators": f"{db_anomalies} veritabanı anomalisi",
                "recommendation": "Parameterized queries kullanın ve input validation uygulayın"
            })
        
        return attacks
    
    def generate_recommendations(self, categorized_anomalies: Dict, severity_count: Dict) -> List[str]:
        """Güvenlik önerileri oluştur"""
        recommendations = []
        
        # Genel öneriler
        if severity_count.get("critical", 0) > 0:
            recommendations.append("🚨 ACIL: Kritik anomaliler tespit edildi. Derhal güvenlik ekibini bilgilendirin.")
        
        if severity_count.get("high", 0) >= 3:
            recommendations.append("⚠️ YÜKSEK: Çoklu yüksek riskli anomali. Sistem güvenliğini gözden geçirin.")
        
        # Kategori bazlı öneriler
        if categorized_anomalies.get("authentication"):
            recommendations.append("🔐 Multi-factor authentication (MFA) implementasyonu önerilir")
            recommendations.append("📊 Başarısız login denemelerini monitör edin")
        
        if categorized_anomalies.get("network"):
            recommendations.append("🌐 Network segmentation ve firewall kurallarını gözden geçirin")
            recommendations.append("📡 Ağ trafiği anomali tespiti sistemlerini devreye alın")
        
        if categorized_anomalies.get("system"):
            recommendations.append("💻 Sistem kaynaklarını monitör edin ve alerting kurun")
            recommendations.append("🔄 Regular sistem güncellemeleri ve patch management")
        
        if categorized_anomalies.get("access_control"):
            recommendations.append("🛡️ Role-based access control (RBAC) implementasyonu")
            recommendations.append("📋 Kullanıcı yetki auditlerini düzenli yapın")
        
        if categorized_anomalies.get("database"):
            recommendations.append("🗄️ Database activity monitoring (DAM) sistemleri kurun")
            recommendations.append("🔒 Veritabanı encryption ve backup güvenliğini sağlayın")
        
        # Genel güvenlik önerileri
        recommendations.extend([
            "📝 Incident response planınızı güncelleyin",
            "👥 Güvenlik farkındalık eğitimleri düzenleyin",
            "🔍 Regular penetration testing yapın",
            "📊 SIEM çözümleri ile log correlation yapın"
        ])
        
        return recommendations[:10]  # En fazla 10 öneri

# Global model instance
anomaly_detector = LLMLogAnomalyDetector()