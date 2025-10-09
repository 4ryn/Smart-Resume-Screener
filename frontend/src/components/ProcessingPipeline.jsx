import React from 'react';
import { CheckCircle, Loader, Circle } from 'lucide-react';

const ProcessingPipeline = ({ steps, currentStep }) => {
  return (
    <div className="max-w-2xl mx-auto">
      <div className="card">
        <h3 className="text-2xl font-bold mb-8 text-center">Processing Your Data</h3>
        
        <div className="space-y-6">
          {steps.map((step, index) => {
            const isComplete = index < currentStep;
            const isCurrent = index === currentStep;
            const isPending = index > currentStep;

            return (
              <div key={index} className="flex items-center space-x-4">
                <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                  isComplete ? 'bg-green-500' :
                  isCurrent ? 'bg-blue-500 animate-pulse' :
                  'bg-gray-700'
                }`}>
                  {isComplete && <CheckCircle size={24} />}
                  {isCurrent && <Loader className="animate-spin" size={24} />}
                  {isPending && <Circle size={24} className="text-gray-500" />}
                </div>

                <div className="flex-1">
                  <p className={`font-medium ${
                    isComplete ? 'text-green-400' :
                    isCurrent ? 'text-blue-400' :
                    'text-gray-500'
                  }`}>
                    {step}
                  </p>
                  {isCurrent && (
                    <div className="mt-2 w-full bg-gray-700 rounded-full h-2 overflow-hidden">
                      <div className="bg-blue-500 h-full animate-pulse" style={{width: '70%'}}></div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {currentStep === steps.length - 1 && (
          <div className="mt-8 text-center">
            <CheckCircle className="mx-auto text-green-400 mb-4" size={64} />
            <p className="text-xl font-semibold text-green-400">Processing Complete!</p>
            <p className="text-gray-400 mt-2">Redirecting to results...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProcessingPipeline;