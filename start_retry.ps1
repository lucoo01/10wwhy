$python = "C:\Users\admin\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"
$argList = @("review_questions.py", "--workers", "1")
$p = Start-Process -FilePath $python `
  -ArgumentList $argList `
  -RedirectStandardOutput "review_retry.log" `
  -RedirectStandardError "review_retry.err" `
  -WorkingDirectory "C:\app\10wwhy" `
  -WindowStyle Hidden `
  -PassThru
Write-Output "Started retry PID=$($p.Id)"
