import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { X, CheckCircle, AlertTriangle, AlertCircle, Info } from 'lucide-react';

// Toast Context
const ToastContext = createContext();

// Toast Reducer
const toastReducer = (state, action) => {
  switch (action.type) {
    case 'ADD_TOAST':
      return [...state, { ...action.payload, id: Date.now() }];
    case 'REMOVE_TOAST':
      return state.filter(toast => toast.id !== action.payload);
    default:
      return state;
  }
};

// Toast Provider
export const ToastProvider = ({ children }) => {
  const [toasts, dispatch] = useReducer(toastReducer, []);

  const addToast = (toast) => {
    dispatch({ type: 'ADD_TOAST', payload: toast });
    
    // Auto remove after duration
    setTimeout(() => {
      dispatch({ type: 'REMOVE_TOAST', payload: toast.id });
    }, toast.duration || 5000);
  };

  const removeToast = (id) => {
    dispatch({ type: 'REMOVE_TOAST', payload: id });
  };

  return (
    <ToastContext.Provider value={{ addToast, removeToast }}>
      {children}
      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </ToastContext.Provider>
  );
};

// Toast Container
const ToastContainer = ({ toasts, removeToast }) => {
  if (toasts.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {toasts.map(toast => (
        <Toast key={toast.id} toast={toast} onRemove={() => removeToast(toast.id)} />
      ))}
    </div>
  );
};

// Individual Toast Component
const Toast = ({ toast, onRemove }) => {
  const { type, title, message, duration = 5000 } = toast;

  const getToastStyles = () => {
    switch (type) {
      case 'success':
        return 'bg-green-50 border-green-200 text-green-800';
      case 'error':
        return 'bg-red-50 border-red-200 text-red-800';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'info':
        return 'bg-blue-50 border-blue-200 text-blue-800';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-600" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
      case 'info':
        return <Info className="h-5 w-5 text-blue-600" />;
      default:
        return <Info className="h-5 w-5 text-gray-600" />;
    }
  };

  useEffect(() => {
    const timer = setTimeout(onRemove, duration);
    return () => clearTimeout(timer);
  }, [duration, onRemove]);

  return (
    <div className={`max-w-sm w-full border rounded-lg shadow-lg p-4 transition-all duration-300 ${getToastStyles()}`}>
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0">
          {getIcon()}
        </div>
        <div className="flex-1 min-w-0">
          {title && (
            <p className="font-medium text-sm">{title}</p>
          )}
          {message && (
            <p className={`text-sm ${title ? 'mt-1' : ''}`}>{message}</p>
          )}
        </div>
        <button
          onClick={onRemove}
          className="flex-shrink-0 ml-2 p-1 rounded-full hover:bg-black hover:bg-opacity-10 transition-colors"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};

// Hook to use toast
export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};


