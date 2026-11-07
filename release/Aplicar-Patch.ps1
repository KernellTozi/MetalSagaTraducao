param([string]$IsoOriginal = '', [string]$Destino = '', [switch]$SemInterface)
$ErrorActionPreference = 'Stop'
$partial = $null
$ownsPartial = $false
try {
    $baseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $manifest = Get-Content -LiteralPath (Join-Path $baseDir 'manifesto.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    foreach ($name in @($manifest.patch.file, $manifest.decoder.file, $manifest.target.file)) {
        if ([IO.Path]::GetFileName($name) -ne $name) { throw 'Nome de arquivo invalido no manifesto.' }
    }
    $patch = Join-Path $baseDir $manifest.patch.file
    $decoder = Join-Path $baseDir $manifest.decoder.file
    if ((Get-FileHash -LiteralPath $patch -Algorithm SHA256).Hash.ToLowerInvariant() -ne $manifest.patch.sha256) {
        throw 'O patch esta incompleto ou foi alterado. Extraia novamente o pacote.'
    }
    if ((Get-FileHash -LiteralPath $decoder -Algorithm SHA256).Hash.ToLowerInvariant() -ne $manifest.decoder.sha256) {
        throw 'O aplicador xdelta foi alterado. Extraia novamente o pacote.'
    }
    if ([string]::IsNullOrWhiteSpace($IsoOriginal)) {
        if ($SemInterface) { throw 'Informe -IsoOriginal.' }
        Add-Type -AssemblyName System.Windows.Forms
        $dialog = New-Object System.Windows.Forms.OpenFileDialog
        $dialog.Title = 'Escolha a ISO ORIGINAL americana do Metal Saga'
        $dialog.Filter = 'Imagem ISO (*.iso)|*.iso'
        if ($dialog.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) { exit 2 }
        $IsoOriginal = $dialog.FileName
        $dialog.Dispose()
    }
    $source = Get-Item -LiteralPath $IsoOriginal
    if ($source.PSIsContainer -or $source.Length -ne $manifest.source.size) {
        throw 'ISO incompativel. Use a imagem original indicada no LEIA-ME.txt, sem outro patch.'
    }
    Write-Host 'Conferindo a ISO original...'
    $sourceHash = (Get-FileHash -LiteralPath $source.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($sourceHash -ne $manifest.source.sha256) {
        throw 'A ISO nao corresponde a versao original exigida. Consulte o SHA-256 no LEIA-ME.txt.'
    }
    if ([string]::IsNullOrWhiteSpace($Destino)) {
        $Destino = Join-Path $source.DirectoryName $manifest.target.file
    }
    $Destino = [IO.Path]::GetFullPath($Destino)
    if ($Destino -eq $source.FullName -or (Test-Path -LiteralPath $Destino)) {
        throw 'O destino ja existe. Escolha outro nome; nenhum arquivo sera sobrescrito.'
    }
    $partial = $Destino + '.partial'
    if (Test-Path -LiteralPath $partial) { throw 'Existe uma aplicacao parcial nesse destino. Escolha outro nome.' }
    if (-not (Test-Path -LiteralPath (Split-Path -Parent $Destino) -PathType Container)) {
        throw 'A pasta de destino nao existe.'
    }
    Write-Host 'Aplicando a traducao em uma nova ISO...'
    # Explicit operands; no shell-built command and no output overwrite flag.
    $ownsPartial = $true
    & $decoder '-D' '-R' '-d' '-s' $source.FullName $patch $partial
    if ($LASTEXITCODE -ne 0) { throw 'O xdelta nao conseguiu aplicar o patch.' }
    $result = Get-Item -LiteralPath $partial
    if ($result.Length -ne $manifest.target.size) { throw 'A nova ISO ficou com tamanho incorreto.' }
    $resultHash = (Get-FileHash -LiteralPath $partial -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($resultHash -ne $manifest.target.sha256) { throw 'A verificacao da nova ISO falhou.' }
    Move-Item -LiteralPath $partial -Destination $Destino
    $partial = $null
    $ownsPartial = $false
    Write-Host ('Concluido: ' + $Destino)
    Write-Host 'ISO original preservada. A nova ISO foi conferida por SHA-256.'
    if (-not $SemInterface) {
        Add-Type -AssemblyName System.Windows.Forms
        [void][System.Windows.Forms.MessageBox]::Show(('Traducao aplicada e conferida.' + [Environment]::NewLine + $Destino), 'Metal Saga PT-BR')
    }
    exit 0
} catch {
    Write-Host ('ERRO: ' + $_.Exception.Message) -ForegroundColor Red
    if ($ownsPartial -and $partial -and (Test-Path -LiteralPath $partial)) { Remove-Item -LiteralPath $partial }
    if (-not $SemInterface) {
        Add-Type -AssemblyName System.Windows.Forms
        [void][System.Windows.Forms.MessageBox]::Show($_.Exception.Message, 'Metal Saga PT-BR')
    }
    exit 1
}
