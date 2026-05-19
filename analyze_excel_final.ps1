# Script PowerShell para analisar estrutura do Excel
$excelFile = "C:\01-Pessoais\01-ControleReprodução\data\cattle_control.xlsx"

Write-Host "Analisando: $excelFile"
Write-Host "Arquivo existe: $(Test-Path $excelFile)"
Write-Host ""

if (-not (Test-Path $excelFile)) {
    Write-Host "ERRO: Arquivo não encontrado!" -ForegroundColor Red
    exit 1
}

# Criar objeto Excel COM
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
Write-Host "Excel aberto..." -ForegroundColor Green

try {
    # Abrir workbook
    $workbook = $excel.Workbooks.Open($excelFile)
    Write-Host "Workbook aberto com sucesso!" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "=" * 80
    Write-Host "ABAS DO WORKBOOK:" -ForegroundColor Cyan
    Write-Host "=" * 80
    
    $i = 1
    foreach ($sheet in $workbook.Sheets) {
        Write-Host "$i. $($sheet.Name)"
        $i++
    }
    
    Write-Host ""
    Write-Host "=" * 80
    Write-Host "ANALISE DE CADA ABA:" -ForegroundColor Cyan
    Write-Host "=" * 80
    
    foreach ($sheet in $workbook.Sheets) {
        Write-Host ""
        Write-Host ""
        Write-Host ("=" * 80)
        Write-Host "ABA: $($sheet.Name)" -ForegroundColor Yellow
        Write-Host ("=" * 80)
        
        $usedRange = $sheet.UsedRange
        $lastRow = $usedRange.Rows.Count
        $lastCol = $usedRange.Columns.Count
        
        Write-Host "Dimensoes: Linhas = $lastRow, Colunas = $lastCol"
        Write-Host ""
        
        # Headers (primeira linha)
        Write-Host "Colunas detectadas:" -ForegroundColor Magenta
        for ($col = 1; $col -le $lastCol; $col++) {
            $cellValue = $sheet.Cells.Item(1, $col).Value2
            if ($cellValue) {
                Write-Host "  $col. $cellValue"
            }
        }
        
        # Primeiras linhas de dados
        Write-Host ""
        Write-Host "Primeiras linhas de dados (amostra):" -ForegroundColor Magenta
        $maxRows = [Math]::Min(5, $lastRow - 1)
        for ($row = 2; $row -le $maxRows + 1; $row++) {
            $rowData = @()
            for ($col = 1; $col -le $lastCol; $col++) {
                $cellValue = $sheet.Cells.Item($row, $col).Value2
                if ($cellValue -ne $null) {
                    if ($cellValue -is [DateTime]) {
                        $rowData += $cellValue.ToString("dd/MM/yyyy")
                    } else {
                        $rowData += "$cellValue"
                    }
                } else {
                    $rowData += "[--]"
                }
            }
            Write-Host "  Linha $row : $($rowData -join ' | ')"
        }
        
        Write-Host ""
        Write-Host "Total de registros: $($lastRow - 1) (excluindo header)" -ForegroundColor Cyan
    }
    
    Write-Host ""
    Write-Host "=" * 80
    Write-Host "ANALISE COMPLETA COM SUCESSO" -ForegroundColor Green
    Write-Host "=" * 80
    
}
catch {
    Write-Host "ERRO NA ANALISE: $_" -ForegroundColor Red
    Write-Host $_.Exception.StackTrace
}
finally {
    Write-Host ""
    Write-Host "Fechando workbook..." -ForegroundColor Cyan
    if ($workbook) {
        $workbook.Close($false)
    }
    if ($excel) {
        $excel.Quit()
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
    }
    Write-Host "Fechado com sucesso." -ForegroundColor Green
}
