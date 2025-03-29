interface Form {
  id: string;
  code: string; // Ví dụ: A110, A120,...
  name: string;
  stage: FormStage;
  status: FormStatus;
  data: any; // Dữ liệu form
  attachments: string[]; // Danh sách file đính kèm
  createdBy: string;
  updatedBy: string;
  createdAt: Date;
  updatedAt: Date;
}

enum FormStage {
  PLANNING = 'PLANNING',
  EXECUTION = 'EXECUTION',
  REPORTING = 'REPORTING'
}

enum FormStatus {
  NOT_STARTED = 'NOT_STARTED',
  IN_PROGRESS = 'IN_PROGRESS', 
  COMPLETED = 'COMPLETED'
} 