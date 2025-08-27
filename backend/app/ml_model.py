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
        results = []
        anomaly_count = 0
        critical_count = 0
        
        # Her satırı kontrol et
        for i, line in enumerate(lines, 1):
            if line.strip():  # Boş satırları atla
                is_anomaly = False
                severity = "info"
                explanation = "Normal log"
                
                line_lower = line.lower()
                
                # Anomali kontrolü
                if any(word in line_lower for word in ['error', 'critical', 'fail', 'exception', 'timeout']):
                    is_anomaly = True
                    anomaly_count += 1
                    
                    if 'critical' in line_lower or 'fatal' in line_lower:
                        severity = "critical"
                        critical_count += 1
                        explanation = "Kritik hata tespit edildi"
                    elif 'error' in line_lower or 'exception' in line_lower:
                        severity = "high"
                        explanation = "Hata tespit edildi"
                    else:
                        severity = "medium"
                        explanation = "Potansiyel sorun tespit edildi"
                
                results.append({
                    "line_number": i,
                    "is_anomaly": is_anomaly,
                    "severity": severity,
                    "anomaly_type": "keyword_detection" if is_anomaly else "normal",
                    "confidence": 0.8 if is_anomaly else 0.9,
                    "explanation": explanation,
                    "log_content": line.strip()
                })
        
        return {
            "results": results,
            "summary": {
                "total_lines": len(results),
                "anomaly_count": anomaly_count,
                "critical_count": critical_count
            }
        }
    
    def predict(self, log_lines: List[str], analysis_type: str = "fast") -> Dict:
        """Log satırları için anomali tahmini yap"""
        try:
            if not log_lines:
                return {"status": "error", "message": "Log satırları boş"}
            
            logger.info(f"LLM ile anomali analizi başlıyor... {len(log_lines)} satır")
            
            # Analiz türüne göre sampling
            if analysis_type == "fast" and len(log_lines) > 500:
                logger.info(f"Hızlı analiz: Büyük dosya ({len(log_lines)} satır), akıllı sampling uygulanıyor")
                log_lines = self.smart_sample_logs(log_lines, target_size=300)
                logger.info(f"Sampling sonrası: {len(log_lines)} satır")
            elif analysis_type == "detailed" and len(log_lines) > 2000:
                logger.info(f"Detaylı analiz: Çok büyük dosya ({len(log_lines)} satır), sınırlı sampling uygulanıyor")
                log_lines = self.smart_sample_logs(log_lines, target_size=1500)
                logger.info(f"Sampling sonrası: {len(log_lines)} satır")
            else:
                logger.info(f"Analiz türü: {analysis_type}, Sampling uygulanmıyor ({len(log_lines)} satır)")
            
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
                        # Line number'ları düzelt (1-based to 0-based)
                        batch_line_idx = result.get("line_number", 1) - 1
                        global_line_number = i + batch_line_idx + 1
                        
                        result["line_number"] = global_line_number
                        result["log_content"] = batch[batch_line_idx] if 0 <= batch_line_idx < len(batch) else ""
                        
                        if result.get("is_anomaly", False):
                            total_anomalies += 1
                            
                            # MITRE teknik ekle
                            mitre_technique = self.get_mitre_technique(
                                result.get("log_content", ""), 
                                result.get("explanation", "")
                            )
                            result["mitre_technique"] = mitre_technique
                            
                            # Enhanced severity hesaplama
                            enhanced_severity = self.calculate_enhanced_severity(
                                result.get("log_content", ""),
                                result.get("explanation", ""),
                                mitre_technique
                            )
                            result["severity"] = enhanced_severity  # Override original severity
                            
                            # Critical count'u enhanced severity'ye göre hesapla
                            if enhanced_severity == "critical":
                                total_critical += 1
                            
                            # Aksiyon önerileri
                            actions = self.generate_action_recommendations(
                                mitre_technique, 
                                enhanced_severity,
                                result.get("log_content", "")
                            )
                            result["recommended_actions"] = actions
                        
                        all_results.append(result)
            
            # Güvenli rapor oluştur (hata ayıklama için basitleştirildi)
            try:
                report = self.generate_security_report(all_results, log_lines)
            except Exception as e:
                logger.error(f"Security report hatası: {str(e)}")
                report = {"error": "Security report oluşturulamadı"}
            
            # Güvenli confidence score hesapla
            try:
                confidence_score = self.calculate_confidence_score(all_results)
            except Exception as e:
                logger.error(f"Confidence score hatası: {str(e)}")
                confidence_score = 0.5
            
            return {
                "status": "success",
                "total_lines": len(log_lines),
                "anomaly_count": total_anomalies,
                "critical_count": total_critical,
                "anomaly_rate": total_anomalies / len(log_lines) if len(log_lines) > 0 else 0,
                "confidence_score": confidence_score,
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
    
    def get_mitre_technique(self, log_content: str, explanation: str) -> Dict:
        """Log içeriğine göre MITRE ATT&CK tekniği belirle"""
        # None kontrolü ekle
        content_lower = (log_content or "").lower()
        explanation_lower = (explanation or "").lower()
        
        # MITRE ATT&CK teknik mapping'i
        mitre_patterns = {
            "T1110": {  # Brute Force
                "name": "Brute Force",
                "tactic": "Credential Access",
                "patterns": ["failed login", "authentication failed", "invalid password", "login attempt", "brute force"]
            },
            "T1190": {  # Exploit Public-Facing Application
                "name": "Exploit Public-Facing Application", 
                "tactic": "Initial Access",
                "patterns": ["sql injection", "xss", "code injection", "exploit", "vulnerability"]
            },
            "T1083": {  # File and Directory Discovery
                "name": "File and Directory Discovery",
                "tactic": "Discovery", 
                "patterns": ["directory traversal", "file access", "path disclosure", "directory listing"]
            },
            "T1005": {  # Data from Local System
                "name": "Data from Local System",
                "tactic": "Collection",
                "patterns": ["data exfil", "sensitive data", "file download", "data extraction"]
            },
            "T1498": {  # Network Denial of Service
                "name": "Network Denial of Service",
                "tactic": "Impact",
                "patterns": ["ddos", "dos attack", "flood", "overload", "exhausted"]
            },
            "T1055": {  # Process Injection
                "name": "Process Injection",
                "tactic": "Defense Evasion",
                "patterns": ["malware", "trojan", "virus", "suspicious process", "injection"]
            },
            "T1078": {  # Valid Accounts
                "name": "Valid Accounts", 
                "tactic": "Persistence",
                "patterns": ["privilege escalation", "unauthorized access", "admin access", "elevated privileges"]
            },
            "T1046": {  # Network Service Scanning
                "name": "Network Service Scanning",
                "tactic": "Discovery",
                "patterns": ["port scan", "network scan", "service discovery", "reconnaissance"]
            }
        }
        
        # Pattern matching
        for technique_id, technique_info in mitre_patterns.items():
            for pattern in technique_info["patterns"]:
                if pattern in content_lower or pattern in explanation_lower:
                    return {
                        "technique_id": technique_id,
                        "technique_name": technique_info["name"],
                        "tactic": technique_info["tactic"],
                        "confidence": 0.8
                    }
        
        return {
            "technique_id": "T1000", 
            "technique_name": "Unknown",
            "tactic": "Unknown",
            "confidence": 0.3
        }
    
    def calculate_enhanced_severity(self, log_content: str, explanation: str, mitre_technique: Dict) -> str:
        """Gelişmiş severity hesaplama - MITRE teknik + etki alanına göre"""
        # None kontrolü ekle
        content_lower = (log_content or "").lower()
        explanation_lower = (explanation or "").lower()
        technique_id = mitre_technique.get("technique_id", "")
        
        severity_score = 0
        
        # MITRE tekniğine göre base severity
        critical_techniques = ["T1190", "T1055", "T1005"]  # Exploit, Malware, Data Exfil
        high_techniques = ["T1110", "T1498", "T1078"]      # Brute Force, DDoS, Privilege Esc
        medium_techniques = ["T1083", "T1046"]              # Discovery, Scanning
        
        if technique_id in critical_techniques:
            severity_score += 40
        elif technique_id in high_techniques:
            severity_score += 25
        elif technique_id in medium_techniques:
            severity_score += 10
        
        # Keyword-based severity boost
        critical_keywords = ["critical", "breach", "compromise", "malware", "exfiltration", "injection"]
        high_keywords = ["failed", "denied", "attack", "intrusion", "unauthorized", "exploit"]
        medium_keywords = ["warning", "error", "timeout", "blocked"]
        
        for keyword in critical_keywords:
            if keyword in content_lower or keyword in explanation_lower:
                severity_score += 30
                break
        
        for keyword in high_keywords:
            if keyword in content_lower or keyword in explanation_lower:
                severity_score += 20
                break
                
        for keyword in medium_keywords:
            if keyword in content_lower or keyword in explanation_lower:
                severity_score += 10
                break
        
        # Frequency/rate based adjustment (multiple events)
        if any(freq_word in explanation_lower for freq_word in ["multiple", "repeated", "frequent", "burst"]):
            severity_score += 15
        
        # System impact assessment
        if any(sys_word in content_lower for sys_word in ["database", "server", "admin", "root", "system"]):
            severity_score += 10
        
        # Final severity determination
        if severity_score >= 60:
            return "critical"
        elif severity_score >= 40:
            return "high"  
        elif severity_score >= 20:
            return "medium"
        else:
            return "low"
    
    def generate_action_recommendations(self, mitre_technique: Dict, severity: str, log_content: str) -> List[str]:
        """MITRE tekniğine göre aksiyon önerileri oluştur"""
        recommendations = []
        technique_id = mitre_technique.get("technique_id", "")
        
        # Genel öneriler
        if severity in ["critical", "high"]:
            recommendations.append("🚨 Acil müdahale gerekli - SOC ekibini bilgilendir")
        
        # Teknik-spesifik öneriler
        if technique_id == "T1110":  # Brute Force
            recommendations.extend([
                "🔒 Kaynak IP adresini geçici olarak blokla",
                "👤 Hedef kullanıcı hesabını geçici kilitle", 
                "📊 Son 24 saatteki benzer denemeleri incele",
                "🛡️ Rate limiting kurallarını güçlendir"
            ])
        elif technique_id == "T1190":  # Exploit
            recommendations.extend([
                "🔧 Uygulama güvenlik yamalarını kontrol et",
                "🚫 İlgili endpoint'i geçici devre dışı bırak",
                "🔍 WAF kurallarını güncelle",
                "📝 Penetrasyon testi planla"
            ])
        elif technique_id == "T1498":  # DDoS
            recommendations.extend([
                "🛡️ DDoS koruma servisini aktifleştir",
                "📊 Trafik analizi yap",
                "🚫 Kaynak IP aralığını blokla",
                "⚡ Yük dengeleyici ayarlarını optimize et"
            ])
        elif technique_id == "T1055":  # Malware
            recommendations.extend([
                "🦠 Antivirüs taraması başlat",
                "🔒 Etkilenen sistemi izole et",
                "💾 Sistem imajı yedekle",
                "🔍 IOC'leri threat intelligence ile karşılaştır"
            ])
        elif technique_id == "T1078":  # Privilege Escalation
            recommendations.extend([
                "👤 Kullanıcı yetkilerini gözden geçir",
                "🔐 Privileged account'ları audit et",
                "📝 Access control matrix'i güncelle",
                "🔍 Son erişim loglarını incele"
            ])
        else:
            recommendations.extend([
                "📊 Benzer olayları korelasyon analizi ile incele",
                "📝 Incident response playbook'u uygula",
                "🔍 Forensik analiz için logları koru"
            ])
        
        return recommendations
    
    def calculate_confidence_score(self, analysis_results: List[Dict]) -> float:
        """Analiz güven skoru hesapla (eşleşen kural/pattern sayısına göre)"""
        if not analysis_results:
            return 0.0
        
        # Anomali tespitlerinin güven skorlarını hesapla
        total_confidence = 0
        valid_results = 0
        
        for result in analysis_results:
            if result.get("is_anomaly"):
                # Açıklama detayına göre güven skoru hesapla
                explanation = result.get("explanation", "").lower()
                confidence = 50  # Base confidence
                
                # Specific patterns increase confidence
                if any(keyword in explanation for keyword in ["error", "failed", "denied", "blocked"]):
                    confidence += 20
                if any(keyword in explanation for keyword in ["attack", "malware", "intrusion", "breach"]):
                    confidence += 25
                if any(keyword in explanation for keyword in ["critical", "severe", "high"]):
                    confidence += 15
                
                # Severity based confidence adjustment
                severity = result.get("severity", "medium")
                if severity == "critical":
                    confidence += 10
                elif severity == "high":
                    confidence += 5
                
                total_confidence += min(confidence, 100)
                valid_results += 1
            else:
                # Normal logs have higher confidence
                total_confidence += 85
                valid_results += 1
        
        return round(total_confidence / valid_results, 1) if valid_results > 0 else 0.0
    
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