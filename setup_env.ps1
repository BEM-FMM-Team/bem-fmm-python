$nproc = (Get-CimInstance -ClassName Win32_Processor | Measure-Object -Property NumberOfLogicalProcessors -Sum).Sum
$threads = $nproc - 0

$env:MKL_NUM_THREADS = "$threads"
$env:OMP_NUM_THREADS = "$threads"

if ($env:PYTHONPATH) {
    $env:PYTHONPATH = "$env:PYTHONPATH;$PWD"
} else {
    $env:PYTHONPATH = "$PWD"
}

if (!(Test-Path "venv")) {
    python -m venv venv
    & ".\venv\Scripts\Activate.ps1"
    pip install -r requirements.txt
} else {
    & ".\venv\Scripts\Activate.ps1"
}
