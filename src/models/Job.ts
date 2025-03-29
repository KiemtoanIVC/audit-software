interface Job {
  id: string;
  clientName: string;
  contractNumber: string;
  contractDate: Date;
  auditPeriod: string;
  industry: string;
  status: JobStatus;
  path: string; // Đường dẫn OneDrive
  forms: Form[];
  createdAt: Date;
  updatedAt: Date;
}

enum JobStatus {
  PLANNING = 'PLANNING',
  EXECUTION = 'EXECUTION', 
  REPORTING = 'REPORTING',
  REVIEW = 'REVIEW',
  COMPLETED = 'COMPLETED'
} 