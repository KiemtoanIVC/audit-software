class FormManager {
  private oneDriveService: OneDriveService;
  private validationService: ValidationService;

  constructor(
    oneDriveService: OneDriveService,
    validationService: ValidationService
  ) {
    this.oneDriveService = oneDriveService;
    this.validationService = validationService;
  }

  async saveForm(jobId: string, form: Form): Promise<void> {
    // Validate form data
    await this.validationService.validateForm(form);

    // Lưu form vào thư mục tương ứng trên OneDrive
    const formPath = `${jobId}/MauBieu/${form.code}`;
    await this.oneDriveService.saveFile(formPath, form);

    // Cập nhật trạng thái job nếu cần
    await this.updateJobStatus(jobId);
  }

  async checkFormsCompletion(jobId: string): Promise<boolean> {
    const forms = await this.getJobForms(jobId);
    return forms.every(form => form.status === FormStatus.COMPLETED);
  }
} 