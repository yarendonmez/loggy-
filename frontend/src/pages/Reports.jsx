import React, { useState, useEffect, useCallback } from 'react';
import { 
  FileText, 
  Shield, 
  AlertTriangle, 
  Clock,
  Download,
  Eye,
  Search
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { useToast } from '../components/ui/toast';
import Navbar from '../components/Navbar';

const Reports = () => {
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterLevel, setFilterLevel] = useState('all');
  const { addToast } = useToast();

  const loadReports = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8000/api/reports');
      if (response.ok) {
        const data = await response.json();
        setReports(data.reports || []);
      }
    } catch (error) {
      console.error('Reports load error:', error);
      addToast({
        type: 'error',
        title: 'Rapor Yükleme Hatası',
        message: 'Raporlar yüklenemedi',
        duration: 5000
      });
    } finally {
      setLoading(false);
    }
  }, [addToast]);

  useEffect(() => {
    loadReports();
  }, [loadReports]);



  const getRiskBadge = (riskLevel) => {
    const colors = {
      'CRITICAL': 'bg-red-500 text-white',
      'HIGH': 'bg-orange-500 text-white',
      'MEDIUM': 'bg-yellow-500 text-black',
      'LOW': 'bg-blue-500 text-white',
      'MINIMAL': 'bg-green-500 text-white'
    };
    return colors[riskLevel] || 'bg-gray-500 text-white';
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'CRITICAL': return <AlertTriangle className="h-4 w-4 text-red-500" />;
      case 'HIGH': return <AlertTriangle className="h-4 w-4 text-orange-500" />;
      case 'MEDIUM': return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'LOW': return <AlertTriangle className="h-4 w-4 text-blue-500" />;
      default: return <Shield className="h-4 w-4 text-green-500" />;
    }
  };

  const filteredReports = reports.filter(report => {
    const matchesSearch = report.filename?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         report.security_report?.summary?.risk_level?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterLevel === 'all' || report.security_report?.summary?.risk_level === filterLevel;
    return matchesSearch && matchesFilter;
  });

  const downloadReport = async (reportId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/reports/${reportId}/download`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `security_report_${reportId}.json`;
        a.click();
        window.URL.revokeObjectURL(url);
        
        addToast({
          type: 'success',
          title: 'Rapor İndirildi',
          message: 'Güvenlik raporu başarıyla indirildi',
          duration: 3000
        });
      }
    } catch (error) {
      addToast({
        type: 'error',
        title: 'İndirme Hatası',
        message: 'Rapor indirilemedi',
        duration: 5000
      });
    }
  };

  if (selectedReport) {
    return <ReportDetail report={selectedReport} onBack={() => setSelectedReport(null)} />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Güvenlik Raporları</h1>
          <p className="text-gray-600 mt-2">AI tabanlı log analizi ve siber güvenlik raporları</p>
        </div>

        {/* Filters */}
        <div className="mb-6 flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Rapor ara..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <select
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            value={filterLevel}
            onChange={(e) => setFilterLevel(e.target.value)}
          >
            <option value="all">Tüm Risk Seviyeleri</option>
            <option value="CRITICAL">Kritik</option>
            <option value="HIGH">Yüksek</option>
            <option value="MEDIUM">Orta</option>
            <option value="LOW">Düşük</option>
            <option value="MINIMAL">Minimal</option>
          </select>
        </div>

        {/* Reports Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {loading ? (
            // Loading skeleton
            [...Array(6)].map((_, i) => (
              <Card key={i} className="animate-pulse">
                <CardHeader>
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="h-3 bg-gray-200 rounded"></div>
                    <div className="h-3 bg-gray-200 rounded w-5/6"></div>
                  </div>
                </CardContent>
              </Card>
            ))
          ) : filteredReports.length === 0 ? (
            <div className="col-span-full text-center py-12">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Henüz rapor yok</h3>
              <p className="text-gray-600">Log analizi yaptıktan sonra raporlar burada görünecek</p>
            </div>
          ) : (
            filteredReports.map((report, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg flex items-center gap-2">
                        <FileText className="h-5 w-5" />
                        {report.filename || `Rapor #${index + 1}`}
                      </CardTitle>
                      <CardDescription className="flex items-center gap-2 mt-2">
                        <Clock className="h-4 w-4" />
                        {new Date(report.created_at).toLocaleString('tr-TR')}
                      </CardDescription>
                    </div>
                    {report.security_report?.summary?.risk_level && (
                      <Badge className={`${getRiskBadge(report.security_report.summary.risk_level)} ml-2`}>
                        {getSeverityIcon(report.security_report.summary.risk_level)}
                        <span className="ml-1">{report.security_report.summary.risk_level}</span>
                      </Badge>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  {report.security_report?.summary && (
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Risk Skoru:</span>
                        <span className="font-semibold text-lg">
                          {report.security_report.summary.risk_score}/100
                        </span>
                      </div>
                      
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Toplam Anomali:</span>
                        <span className="font-medium">
                          {report.security_report.summary.total_anomalies}
                        </span>
                      </div>
                      
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Potansiyel Saldırı:</span>
                        <span className="font-medium text-red-600">
                          {report.security_report.potential_attacks?.length || 0}
                        </span>
                      </div>
                      
                      {/* Progress bar for risk score */}
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${
                            report.security_report.summary.risk_score >= 80 ? 'bg-red-500' :
                            report.security_report.summary.risk_score >= 60 ? 'bg-orange-500' :
                            report.security_report.summary.risk_score >= 40 ? 'bg-yellow-500' :
                            report.security_report.summary.risk_score >= 20 ? 'bg-blue-500' : 'bg-green-500'
                          }`}
                          style={{ width: `${report.security_report.summary.risk_score}%` }}
                        ></div>
                      </div>
                      
                      <div className="flex gap-2 pt-2">
                        <Button 
                          size="sm" 
                          className="flex-1"
                          onClick={() => setSelectedReport(report)}
                        >
                          <Eye className="h-4 w-4 mr-1" />
                          Detayları Gör
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => downloadReport(report.id)}
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

// Rapor detay bileşeni
const ReportDetail = ({ report, onBack }) => {
  const securityReport = report.security_report;
  
  const getRiskBadge = (riskLevel) => {
    const colors = {
      'CRITICAL': 'bg-red-500 text-white',
      'HIGH': 'bg-orange-500 text-white',
      'MEDIUM': 'bg-yellow-500 text-black',
      'LOW': 'bg-blue-500 text-white',
      'MINIMAL': 'bg-green-500 text-white'
    };
    return colors[riskLevel] || 'bg-gray-500 text-white';
  };
  
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-6 flex items-center gap-4">
          <Button variant="outline" onClick={onBack}>
            ← Geri
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {report.filename} - Güvenlik Raporu
            </h1>
            <p className="text-gray-600">
              {new Date(securityReport.timestamp).toLocaleString('tr-TR')}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Summary */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle>Özet</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-center">
                  <div className="text-3xl font-bold mb-2">
                    {securityReport.summary.risk_score}/100
                  </div>
                  <Badge className={`${getRiskBadge(securityReport.summary.risk_level)}`}>
                    {securityReport.summary.risk_level}
                  </Badge>
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Toplam Log:</span>
                    <span className="font-medium">{securityReport.summary.total_logs}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Anomali:</span>
                    <span className="font-medium text-red-600">
                      {securityReport.summary.total_anomalies}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Kritik:</span>
                    <span className="font-medium text-red-800">
                      {securityReport.summary.severity_distribution.critical}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Potential Attacks */}
            {securityReport.potential_attacks?.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-red-600">🚨 Tespit Edilen Potansiyel Saldırılar</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {securityReport.potential_attacks.map((attack, index) => (
                      <div key={index} className="border-l-4 border-red-500 pl-4 py-2">
                        <div className="flex items-center gap-2 mb-2">
                          <AlertTriangle className="h-5 w-5 text-red-500" />
                          <span className="font-semibold">{attack.attack_type}</span>
                          <Badge variant="destructive">{attack.severity}</Badge>
                        </div>
                        <p className="text-gray-700 mb-2">{attack.description}</p>
                        <p className="text-sm text-gray-600 mb-2">
                          <strong>Göstergeler:</strong> {attack.indicators}
                        </p>
                        <p className="text-sm text-blue-700">
                          <strong>Öneri:</strong> {attack.recommendation}
                        </p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Recommendations */}
            <Card>
              <CardHeader>
                <CardTitle>💡 Güvenlik Önerileri</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {securityReport.recommendations.map((rec, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <span className="text-blue-500 mt-1">•</span>
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            {/* Attack Categories */}
            <Card>
              <CardHeader>
                <CardTitle>📊 Saldırı Kategorileri</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(securityReport.attack_categories).map(([category, count]) => (
                    <div key={category} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                      <span className="capitalize">{category.replace('_', ' ')}</span>
                      <Badge variant="outline">{count}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Analysis Methodology */}
            <Card>
              <CardHeader>
                <CardTitle>🔍 Analiz Metodolojisi</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="font-semibold mb-2">AI Modeli:</h4>
                  <p>{securityReport.analysis_methodology.ai_model}</p>
                </div>
                
                <div>
                  <h4 className="font-semibold mb-2">Analiz Kriterleri:</h4>
                  <ul className="list-disc list-inside space-y-1">
                    {securityReport.analysis_methodology.analysis_criteria.map((criteria, index) => (
                      <li key={index} className="text-sm">{criteria}</li>
                    ))}
                  </ul>
                </div>
                
                <div>
                  <h4 className="font-semibold mb-2">Tespit Desenleri:</h4>
                  <ul className="list-disc list-inside space-y-1">
                    {securityReport.analysis_methodology.detection_patterns.map((pattern, index) => (
                      <li key={index} className="text-sm">{pattern}</li>
                    ))}
                  </ul>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Reports;
