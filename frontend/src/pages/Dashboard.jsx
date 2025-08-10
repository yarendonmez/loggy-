import React from 'react';
import { Link } from 'react-router-dom';
import { 
  BarChart3, 
  Upload, 
  Activity, 
  AlertTriangle,
  TrendingUp,
  FileText,
  Clock,
  Server,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import Navbar from '../components/Navbar';

const Dashboard = () => {
  // Mock data - gerçek uygulamada API'den gelecek
  const stats = {
    totalLogs: 1247,
    anomalies: 23,
    criticalIssues: 3,
    systemsMonitored: 8
  };

  const recentAnomalies = [
    {
      id: 1,
      timestamp: '2024-01-15 14:32:15',
      severity: 'critical',
      message: 'Database connection timeout detected',
      system: 'Production DB'
    },
    {
      id: 2,
      timestamp: '2024-01-15 14:28:42',
      severity: 'warning',
      message: 'High CPU usage on server-02',
      system: 'Web Server'
    },
    {
      id: 3,
      timestamp: '2024-01-15 14:25:18',
      severity: 'info',
      message: 'Unusual login pattern detected',
      system: 'Auth Service'
    }
  ];

  const systemStatus = [
    { name: 'Web Server', status: 'healthy', uptime: '99.8%' },
    { name: 'Database', status: 'warning', uptime: '95.2%' },
    { name: 'Auth Service', status: 'healthy', uptime: '99.9%' },
    { name: 'File Storage', status: 'healthy', uptime: '99.7%' }
  ];

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'warning': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'info': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy': return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'warning': return <AlertCircle className="h-4 w-4 text-yellow-600" />;
      case 'error': return <XCircle className="h-4 w-4 text-red-600" />;
      default: return <Clock className="h-4 w-4 text-gray-600" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-2">Sistem loglarınızın genel durumu ve anomali tespitleri</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Toplam Log</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalLogs.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                Son 24 saat
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Anomaliler</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">{stats.anomalies}</div>
              <p className="text-xs text-muted-foreground">
                Tespit edilen
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Kritik Sorunlar</CardTitle>
              <XCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{stats.criticalIssues}</div>
              <p className="text-xs text-muted-foreground">
                Acil müdahale gerekli
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">İzlenen Sistemler</CardTitle>
              <Server className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.systemsMonitored}</div>
              <p className="text-xs text-muted-foreground">
                Aktif izleme
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Recent Anomalies */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <AlertTriangle className="h-5 w-5 text-orange-600" />
                  <span>Son Anomaliler</span>
                </CardTitle>
                <CardDescription>
                  Son 24 saatte tespit edilen anomali kayıtları
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentAnomalies.map((anomaly) => (
                    <div key={anomaly.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className={`p-2 rounded-full ${getSeverityColor(anomaly.severity)}`}>
                          <AlertTriangle className="h-4 w-4" />
                        </div>
                        <div>
                          <p className="font-medium text-sm">{anomaly.message}</p>
                          <p className="text-xs text-gray-500">{anomaly.system} • {anomaly.timestamp}</p>
                        </div>
                      </div>
                      <Badge variant={anomaly.severity === 'critical' ? 'destructive' : 'secondary'}>
                        {anomaly.severity}
                      </Badge>
                    </div>
                  ))}
                </div>
                <div className="mt-4">
                  <Button variant="outline" className="w-full">
                    Tüm Anomalileri Görüntüle
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions & System Status */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Hızlı İşlemler</CardTitle>
                <CardDescription>
                  Sık kullanılan işlemler
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <Link to="/upload">
                  <Button className="w-full justify-start" size="lg">
                    <Upload className="mr-2 h-4 w-4" />
                    Yeni Log Yükle
                  </Button>
                </Link>
                <Link to="/analysis">
                  <Button variant="outline" className="w-full justify-start" size="lg">
                    <Activity className="mr-2 h-4 w-4" />
                    Analiz Başlat
                  </Button>
                </Link>
                <Button variant="outline" className="w-full justify-start" size="lg">
                  <BarChart3 className="mr-2 h-4 w-4" />
                  Rapor Oluştur
                </Button>
              </CardContent>
            </Card>

            {/* System Status */}
            <Card>
              <CardHeader>
                <CardTitle>Sistem Durumu</CardTitle>
                <CardDescription>
                  İzlenen sistemlerin durumu
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {systemStatus.map((system, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        {getStatusIcon(system.status)}
                        <div>
                          <p className="font-medium text-sm">{system.name}</p>
                          <p className="text-xs text-gray-500">Uptime: {system.uptime}</p>
                        </div>
                      </div>
                      <Badge variant={system.status === 'healthy' ? 'default' : 'secondary'}>
                        {system.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
