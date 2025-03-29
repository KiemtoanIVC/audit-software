def test_create_job():
    controller = JobController()
    job_data = {
        "client_name": "Test Client",
        "contract_number": "TC001"
    }
    job = controller.create_job(job_data)
    assert job.client_name == "Test Client"
    assert job.job_path.exists()
    
def test_open_job():
    pass 