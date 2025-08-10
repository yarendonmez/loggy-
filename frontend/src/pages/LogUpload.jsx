import React, { useState } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle, Download } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import Navbar from '../components/Navbar';

const LogUpload = () => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('idle'); // idle, uploading, success, error

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFile = (file) => {
    // Dosya tipi kontrolü
    const allowedTypes = ['.csv', '.log', '.txt'];
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    
    if (!allowedTypes.includes(fileExtension)) {
      alert('Sadece .csv, .log ve .txt dosyaları desteklenir.');
      return;
    }

    // Dosya boyutu kontrolü (50MB)
    if (file.size > 50 * 1024 * 1024) {
      alert('Dosya boyutu 50MB\'dan küçük olmalıdır.');
      return;
    }

    setSelectedFile(file);
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploadStatus('uploading');
    
    // Mock upload - gerçek uygulamada API'ye gönderilecek
    setTimeout(() => {
      setUploadStatus('success');
    }, 2000);
  };

  const getFileIcon = (fileName) => {
    const extension = fileName?.toLowerCase().substring(fileName.lastIndexOf('.'));
    switch (extension) {
      case '.csv': return <FileText className="h-8 w-8 text-green-600" />;
      case '.log': return <FileText className="h-8 w-8 text-blue-600" />;
      case '.txt': return <FileText className="h-8 w-8 text-gray-600" />;
      default: return <FileText className="h-8 w-8 text-gray-400" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Log Yükle</h1>
          <p className="text-gray-600 mt-2">Analiz için log dosyanızı yükleyin</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Upload Area */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>Dosya Yükleme</CardTitle>
                <CardDescription>
                  Desteklenen formatlar: CSV, LOG, TXT (Maksimum 50MB)
                </CardDescription>
              </CardHeader>
              <CardContent>
                {/* Drag & Drop Area */}
                <div
                  className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                    dragActive 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-lg font-medium text-gray-900 mb-2">
                    Dosyanızı buraya sürükleyin
                  </p>
                  <p className="text-gray-500 mb-4">
                    veya dosya seçmek için tıklayın
                  </p>
                  <input
                    type="file"
                    accept=".csv,.log,.txt"
                    onChange={handleFileInput}
                    className="hidden"
                    id="file-input"
                  />
                  <label htmlFor="file-input">
                    <Button variant="outline" className="cursor-pointer">
                      Dosya Seç
                    </Button>
                  </label>
                </div>

                {/* Selected File */}
                {selectedFile && (
                  <div className="mt-6 p-4 border rounded-lg bg-gray-50">
                    <div className="flex items-center space-x-3">
                      {getFileIcon(selectedFile.name)}
                      <div className="flex-1">
                        <p className="font-medium text-sm">{selectedFile.name}</p>
                        <p className="text-xs text-gray-500">
                          {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setSelectedFile(null)}
                      >
                        Kaldır
                      </Button>
                    </div>
                  </div>
                )}

                {/* Upload Button */}
                {selectedFile && (
                  <div className="mt-6">
                    <Button 
                      onClick={handleUpload}
                      disabled={uploadStatus === 'uploading'}
                      className="w-full"
                      size="lg"
                    >
                      {uploadStatus === 'uploading' ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                          Yükleniyor...
                        </>
                      ) : (
                        <>
                          <Upload className="mr-2 h-4 w-4" />
                          Yükle ve Analiz Et
                        </>
                      )}
                    </Button>
                  </div>
                )}

                {/* Upload Status */}
                {uploadStatus === 'success' && (
                  <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <CheckCircle className="h-5 w-5 text-green-600" />
                      <span className="text-green-800 font-medium">
                        Dosya başarıyla yüklendi!
                      </span>
                    </div>
                    <p className="text-green-700 text-sm mt-1">
                      Analiz sayfasına yönlendiriliyorsunuz...
                    </p>
                  </div>
                )}

                {uploadStatus === 'error' && (
                  <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <AlertCircle className="h-5 w-5 text-red-600" />
                      <span className="text-red-800 font-medium">
                        Yükleme hatası!
                      </span>
                    </div>
                    <p className="text-red-700 text-sm mt-1">
                      Dosya yüklenirken bir hata oluştu. Lütfen tekrar deneyin.
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Info Panel */}
          <div className="space-y-6">
            {/* Supported Formats */}
            <Card>
              <CardHeader>
                <CardTitle>Desteklenen Formatlar</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Badge variant="outline">CSV</Badge>
                  <span className="text-sm text-gray-600">Comma-separated values</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant="outline">LOG</Badge>
                  <span className="text-sm text-gray-600">Log dosyaları</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant="outline">TXT</Badge>
                  <span className="text-sm text-gray-600">Metin dosyaları</span>
                </div>
              </CardContent>
            </Card>

            {/* Requirements */}
            <Card>
              <CardHeader>
                <CardTitle>Gereksinimler</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span className="text-sm">Maksimum dosya boyutu: 50MB</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span className="text-sm">UTF-8 encoding</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span className="text-sm">Satır başına bir log kaydı</span>
                </div>
              </CardContent>
            </Card>

            {/* Sample Download */}
            <Card>
              <CardHeader>
                <CardTitle>Örnek Dosya</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 mb-3">
                  Test için örnek log dosyası indirin
                </p>
                <Button variant="outline" className="w-full">
                  <Download className="mr-2 h-4 w-4" />
                  Örnek CSV İndir
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LogUpload;
