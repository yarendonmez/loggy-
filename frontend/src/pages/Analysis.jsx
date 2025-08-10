import React, { useState } from 'react';
import { Activity, Search, Filter, AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import Navbar from '../components/Navbar';

const Analysis = () => {
  const [analysisStatus, setAnalysisStatus] = useState('idle'); // idle, running, completed
  const [progress, setProgress] = useState(0);

  // Mock analysis data
  const analysisResults = {
    totalLogs: 1247,
    anomalies: 23,
    criticalIssues: 3,
    processingTime: '2.3s',
    topErrors: [
      { error: 'Connection timeout', count: 8, severity: 'critical' },
      { error: 'High CPU usage', count: 5, severity: 'warning' },
      { error: 'Memory leak detected', count: 3, severity: 'info' }
    ]
  };

  const anomalyLogs = [
    {
      id: 1,
      timestamp: '2024-01-15 14:32:15',
      severity: 'critical',
      message: 'Database connection timeout detected on server-01',
      system: 'Production DB',
      confidence: 0.95
    },
    {
      id: 2,
      timestamp: '2024-01-15 14:28:42',
      severity: 'warning',
      message: 'High CPU usage on server-02 (87%)',
      system: 'Web Server',
      confidence: 0.82
    },
    {
      id: 3,
      timestamp: '2024-01-15 14:25:18',
      severity: 'info',
      message: 'Unusual login pattern detected from IP 192.168.1.100',
      system: 'Auth Service',
      confidence: 0.78
    }
  ];

  const startAnalysis = () => {
    setAnalysisStatus('running');
    setProgress(0);
    
    // Mock progress simulation
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setAnalysisStatus('completed');
          return 100;
        }
        return prev + 10;
      });
    }, 200);
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

        {/* Analysis Status */}
        {analysisStatus === 'idle' && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Activity className="h-5 w-5 text-blue-600" />
                <span>Analiz Başlat</span>
              </CardTitle>
              <CardDescription>
                Log dosyanızı analiz etmek için başlat butonuna tıklayın
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={startAnalysis} size="lg" className="w-full">
                <Activity className="mr-2 h-4 w-4" />
                Analizi Başlat
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
                  <div className="text-2xl font-bold">{analysisResults.totalLogs.toLocaleString()}</div>
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
                  <div className="text-2xl font-bold text-orange-600">{analysisResults.anomalies}</div>
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
                  <div className="text-2xl font-bold text-red-600">{analysisResults.criticalIssues}</div>
                  <p className="text-xs text-muted-foreground">
                    Acil müdahale gerekli
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">İşlem Süresi</CardTitle>
                  <Clock className="h-4 w-4 text-blue-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{analysisResults.processingTime}</div>
                  <p className="text-xs text-muted-foreground">
                    Toplam süre
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Top Errors */}
            <Card className="mb-8">
              <CardHeader>
                <CardTitle>En Çok Görülen Hatalar</CardTitle>
                <CardDescription>
                  Analiz sonucunda tespit edilen en yaygın hata türleri
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analysisResults.topErrors.map((error, index) => (
                    <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className={`p-2 rounded-full ${getSeverityColor(error.severity)}`}>
                          <AlertTriangle className="h-4 w-4" />
                        </div>
                        <div>
                          <p className="font-medium text-sm">{error.error}</p>
                          <p className="text-xs text-gray-500">{error.count} kez görüldü</p>
                        </div>
                      </div>
                      <Badge variant={error.severity === 'critical' ? 'destructive' : 'secondary'}>
                        {error.severity}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Anomaly Details */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Anomali Detayları</span>
                  <div className="flex items-center space-x-2">
                    <Search className="h-4 w-4 text-gray-400" />
                    <input 
                      type="text" 
                      placeholder="Anomali ara..."
                      className="px-3 py-1 border rounded-md text-sm"
                    />
                    <Button variant="outline" size="sm">
                      <Filter className="h-4 w-4 mr-1" />
                      Filtrele
                    </Button>
                  </div>
                </CardTitle>
                <CardDescription>
                  Tespit edilen anomali kayıtları ve detayları
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {anomalyLogs.map((log) => (
                    <div key={log.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <div className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(log.severity)}`}>
                              {log.severity}
                            </div>
                            <span className="text-sm text-gray-500">{log.timestamp}</span>
                            <span className="text-sm text-gray-500">•</span>
                            <span className="text-sm text-gray-500">{log.system}</span>
                          </div>
                          <p className="font-medium text-sm mb-1">{log.message}</p>
                          <div className="flex items-center space-x-4 text-xs text-gray-500">
                            <span>Güven: %{(log.confidence * 100).toFixed(0)}</span>
                            <span>ID: #{log.id}</span>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Button variant="outline" size="sm">
                            Detay
                          </Button>
                          <Button variant="outline" size="sm">
                            Raporla
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
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
