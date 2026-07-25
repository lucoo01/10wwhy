$python = "C:\Users\admin\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"
$argList = @("review_questions.py", "--workers", "4")
$p = Start-Process -FilePath $python `
  -ArgumentList $argList `
  -RedirectStandardOutput "review_run.log" `
  -RedirectStandardError "review_run.err" `
  -WorkingDirectory "C:\app\10wwhy" `
  -WindowStyle Hidden `
  -PassThru
Write-Output "Started PID=$($p.Id)"