import React, { useState, useEffect, useCallback } from 'react';
import { Activity, Search, AlertTriangle, CheckCircle, Clock, FileText } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { useToast } from '../components/ui/toast';
import Navbar from '../components/Navbar';
import { useSearchParams } from 'react-router-dom';

const Analysis = () => {
  const [analysisStatus, setAnalysisStatus] = useState('idle'); // idle, running, completed
  const [progress, setProgress] = useState(0);
  const [searchParams] = useSearchParams();
  const [fileId, setFileId] = useState(null);
  const [fileData, setFileData] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [searchFilter, setSearchFilter] = useState('');
  const [severityFilter, setSeverityFilter] = useState('all');
  const [analysisType, setAnalysisType] = useState('fast'); // fast, detailed
  const { addToast } = useToast();


  // URL'den file ID'yi al
  useEffect(() => {
    const urlFileId = searchParams.get('fileId');
    if (urlFileId) {
      setFileId(parseInt(urlFileId));
    }
  }, [searchParams]);

  const loadFileData = useCallback(async () => {
    try {
      console.log('Loading file data for fileId:', fileId);
      const response = await fetch(`http://localhost:8000/api/files`);
      if (response.ok) {
        const data = await response.json();
        console.log('API Response:', data);
        const file = data.files.find(f => f.id === fileId);
        console.log('Found file:', file);
        if (file) {
          setFileData(file);
          if (file.is_analyzed) {
            // Analiz sonuçları zaten var
            setAnalysisStatus('completed');
            loadAnalysisResults();
          }
        }
      }
    } catch (error) {
      console.error('File data load error:', error);
      addToast({
        type: 'error',
        title: 'Veri Yükleme Hatası',
        message: 'Dosya bilgileri yüklenemedi',
        duration: 5000
      });
    }
  }, [fileId, addToast]);

  // Dosya bilgilerini yükle
  useEffect(() => {
    if (fileId) {
      loadFileData();
      loadAnalysisResults();
    }
  }, [fileId, loadFileData]);

  const loadAnalysisResults = async () => {
    if (!fileId) return;
    
    try {
      // Dosya ID'si ile analiz sonuçlarını yükle
      const response = await fetch(`http://localhost:8000/api/analysis/${fileId}/results`);
      if (response.ok) {
        const data = await response.json();
        setAnalysisData(data.summary);
        setAnalysisResults(data.results);
      } else {
        console.log('No analysis results found for this file yet');
        setAnalysisData(null);
        setAnalysisResults([]);
      }
    } catch (error) {
      console.error('Analysis results load error:', error);
      setAnalysisData(null);
      setAnalysisResults([]);
    }
  };

  const startAnalysis = async () => {
    if (!fileId) {
      addToast({
        type: 'error',
        title: 'Dosya Bulunamadı',
        message: 'Analiz edilecek dosya bulunamadı',
        duration: 5000
      });
      return;
    }

    setAnalysisStatus('running');
    setProgress(0);

    try {
      // Progress simulation
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + Math.random() * 15, 90));
      }, 500);

      // API çağrısı (analiz türü ile)
      const response = await fetch(`http://localhost:8000/api/analyze/${fileId}?analysis_type=${analysisType}`, {
        method: 'POST'
      });

      clearInterval(progressInterval);
      setProgress(100);

      if (response.ok) {
        const result = await response.json();
        setAnalysisData(result.summary);
        
        addToast({
          type: 'success',
          title: 'Analiz Tamamlandı!',
          message: `${result.summary.anomaly_count} anomali tespit edildi`,
          duration: 5000
        });

        // Sonuçları yükle
        setTimeout(() => {
          loadAnalysisResults();
          setAnalysisStatus('completed');
        }, 1000);

      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Analiz başarısız');
      }

    } catch (error) {
      console.error('Analysis error:', error);
      setAnalysisStatus('idle');
      setProgress(0);
      
      addToast({
        type: 'error',
        title: 'Analiz Başarısız',
        message: error.message || 'Analiz sırasında bir hata oluştu',
        duration: 5000
      });
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-50 border-red-200';
      case 'warning': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'info': return 'text-blue-600 bg-blue-50 border-blue-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Log Analizi</h1>
          <p className="text-gray-600 mt-2">AI destekli anomali tespiti ve analiz sonuçları</p>
        </div>

        {/* File Info */}
        {fileData && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <FileText className="h-5 w-5 text-blue-600" />
                <span>Dosya Bilgileri</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-gray-500">Dosya Adı</p>
                  <p className="font-medium">{fileData.filename}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Toplam Satır</p>
                  <p className="font-medium">{fileData.total_lines?.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Dosya Boyutu</p>
                  <p className="font-medium">{(fileData.file_size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Analysis Status */}
        {analysisStatus === 'idle' && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Activity className="h-5 w-5 text-blue-600" />
                <span>Analiz Başlat</span>
              </CardTitle>
              <CardDescription>
                {fileData ? `${fileData.filename} dosyasını analiz etmek için başlat butonuna tıklayın` : 'Log dosyanızı analiz etmek için başlat butonuna tıklayın'}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Analiz Türü Seçimi */}
              <div className="space-y-3">
                <label className="text-sm font-medium text-gray-700">Analiz Türü:</label>
                <div className="grid grid-cols-2 gap-3">
                  <div 
                    className={`p-3 rounded-lg border-2 cursor-pointer transition-all ${
                      analysisType === 'fast' 
                        ? 'border-blue-500 bg-blue-50 text-blue-700' 
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setAnalysisType('fast')}
                  >
                    <div className="text-center">
                      <div className="font-medium">⚡ Hızlı Analiz</div>
                      <div className="text-xs text-gray-500 mt-1">
                        ~300 log | 1-2 dk
                      </div>
                    </div>
                  </div>
                  <div 
                    className={`p-3 rounded-lg border-2 cursor-pointer transition-all ${
                      analysisType === 'detailed' 
                        ? 'border-green-500 bg-green-50 text-green-700' 
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setAnalysisType('detailed')}
                  >
                    <div className="text-center">
                      <div className="font-medium">🔍 Detaylı Analiz</div>
                      <div className="text-xs text-gray-500 mt-1">
                        Tüm loglar | 3-10 dk
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <Button onClick={startAnalysis} size="lg" className="w-full" disabled={!fileId || analysisStatus === 'running'}>
                <Activity className="mr-2 h-4 w-4" />
                {analysisType === 'fast' ? '⚡ Hızlı Analizi Başlat' : '🔍 Detaylı Analizi Başlat'}
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Analysis Progress */}
        {analysisStatus === 'running' && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                <span>Analiz Devam Ediyor</span>
              </CardTitle>
              <CardDescription>
                Log dosyanız AI modeli ile analiz ediliyor...
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600 text-center">
                  %{progress} tamamlandı
                </p>
                <div className="text-sm text-gray-500 space-y-1">
                  <p>• Log dosyası okunuyor...</p>
                  <p>• Öznitelik çıkarımı yapılıyor...</p>
                  <p>• AI modeli çalıştırılıyor...</p>
                  <p>• Sonuçlar işleniyor...</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Analysis Results */}
        {analysisStatus === 'completed' && (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Toplam Log</CardTitle>
                  <CheckCircle className="h-4 w-4 text-green-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{analysisData?.total_lines?.toLocaleString() || 0}</div>
                  <p className="text-xs text-muted-foreground">
                    İşlenen kayıt
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Anomaliler</CardTitle>
                  <AlertTriangle className="h-4 w-4 text-orange-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-orange-600">{analysisData?.anomaly_count || 0}</div>
                  <p className="text-xs text-muted-foreground">
                    Tespit edilen
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Kritik Sorunlar</CardTitle>
                  <AlertTriangle className="h-4 w-4 text-red-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-red-600">{analysisData?.critical_count || 0}</div>
                  <p className="text-xs text-muted-foreground">
                    Acil müdahale gerekli
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Anomali Oranı</CardTitle>
                  <Clock className="h-4 w-4 text-blue-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {Number.isFinite(analysisData?.anomaly_rate) ? `%${analysisData.anomaly_rate.toFixed(1)}` : '—'}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Toplam oranı
                  </p>
                </CardContent>
              </Card>

            </div>

            {/* Summary Info */}
            {analysisData && (
              <Card className="mb-8">
                <CardHeader>
                  <CardTitle>
                    Analiz Özeti 
                    <Badge className="ml-2" variant={analysisType === 'fast' ? 'default' : 'secondary'}>
                      {analysisType === 'fast' ? '⚡ Hızlı' : '🔍 Detaylı'}
                    </Badge>
                  </CardTitle>
                  <CardDescription>
                    {analysisType === 'fast' ? 'Hızlı analiz ile önemli anomaliler tespit edildi' : 'Detaylı analiz ile kapsamlı tarama yapıldı'}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <p className="text-sm text-gray-500">Toplam İşlenen Log</p>
                      <p className="text-2xl font-bold">{analysisData.total_lines?.toLocaleString()}</p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm text-gray-500">Tespit Edilen Anomali</p>
                      <p className="text-2xl font-bold text-orange-600">{analysisData.anomaly_count}</p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm text-gray-500">Kritik Seviye</p>
                      <p className="text-2xl font-bold text-red-600">{analysisData.critical_count}</p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm text-gray-500">Anomali Oranı</p>
                      <p className="text-2xl font-bold text-blue-600">%{analysisData.anomaly_rate?.toFixed(2)}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Anomaly Details */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Anomali Detayları</span>
                  <div className="flex items-center space-x-2">
                    <Search className="h-4 w-4 text-gray-400" />
                    <input 
                      type="text" 
                      placeholder="Log içeriğinde ara..."
                      className="px-3 py-1 border rounded-md text-sm"
                      value={searchFilter}
                      onChange={(e) => setSearchFilter(e.target.value)}
                    />
                    <select 
                      className="px-3 py-1 border rounded-md text-sm"
                      value={severityFilter}
                      onChange={(e) => setSeverityFilter(e.target.value)}
                    >
                      <option value="all">Tümü</option>
                      <option value="anomalies">Sadece Anomaliler</option>
                      <option value="critical">Kritik</option>
                      <option value="warning">Uyarı</option>
                      <option value="info">Bilgi</option>
                      <option value="normal">Normal</option>
                    </select>
                  </div>
                </CardTitle>
                <CardDescription>
                  Tespit edilen anomali kayıtları ve detayları
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analysisResults && analysisResults.length > 0 ? (
                    analysisResults
                      .filter(log => {
                        if (severityFilter === 'all') return true;
                        if (severityFilter === 'anomalies') return log.is_anomaly;
                        return log.severity === severityFilter;
                      })
                      .filter(log => 
                        searchFilter === '' || 
                        log.log_content.toLowerCase().includes(searchFilter.toLowerCase())
                      )
                      .slice(0, 20) // İlk 20 sonuç
                      .map((log) => (
                        <div key={log.line_number} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3 mb-2">
                                <div className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(log.severity)}`}>
                                  {log.severity}
                                </div>
                                <span className="text-sm text-gray-500">Satır #{log.line_number}</span>
                                {log.is_anomaly && (
                                  <>
                                    <span className="text-sm text-gray-500">•</span>
                                    <Badge variant="destructive" className="text-xs">ANOMALI</Badge>
                                  </>
                                )}
                              </div>
                              <p className="font-mono text-sm mb-1 bg-gray-100 p-2 rounded">
                                {log.log_content.length > 200 
                                  ? log.log_content.substring(0, 200) + '...' 
                                  : log.log_content
                                }
                              </p>
                              <div className="flex items-center space-x-4 text-xs text-gray-500">
                                <span>Güven: %{(log.confidence * 100).toFixed(0)}</span>
                                <span>Anomali Olasılığı: %{(log.anomaly_probability * 100).toFixed(1)}</span>
                              </div>
                            </div>
                            <div className="flex items-center space-x-2">
                              <Button variant="outline" size="sm">
                                Detay
                              </Button>
                              {log.is_anomaly && (
                                <Button variant="outline" size="sm">
                                  Raporla
                                </Button>
                              )}
                            </div>
                          </div>
                        </div>
                      ))
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-gray-500">Henüz analiz sonucu bulunmuyor.</p>
                      <p className="text-sm text-gray-400 mt-2">
                        Analizi başlatmak için yukarıdaki butonu kullanın.
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </div>
  );
};

export default Analysis;
