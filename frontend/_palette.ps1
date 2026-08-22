$ErrorActionPreference = 'Stop'
$files = @(
    'src\pages\RunsPage.tsx',
    'src\pages\CatalogPage.tsx',
    'src\pages\ValidationPage.tsx',
    'src\pages\ExportPage.tsx'
)

# ordered longest-first replacements: old cool palette -> rose gold system
$map = [ordered]@{
    'bg-brand-500 text-white shadow-sm' = 'bg-rosegold-500 text-white shadow-sm hover:bg-rosegold-600'
    'border-brand-400 bg-indigo-50/50'  = 'border-rosegold-400 bg-rosegold-50'
    'border-brand-400'                  = 'border-rosegold-400'
    'text-teal-600 dark:text-teal-600'  = 'text-gold-700'
    'text-teal-600'                     = 'text-gold-700'
    'text-teal-700'                     = 'text-gold-700'
    'text-teal-500'                     = 'text-gold-600'
    'bg-teal-400'                       = 'bg-gold-400'
    'bg-emerald-500'                    = 'bg-gold-400'
    'text-emerald-600'                  = 'text-gold-700'
    # slate -> warm neutrals (silver/onyx)
    'text-slate-800' = 'text-onyx-700'
    'text-slate-700' = 'text-onyx-600'
    'text-slate-600' = 'text-onyx-500'
    'text-slate-500' = 'text-silver-600'
    'text-slate-400' = 'text-silver-500'
    'text-slate-300' = 'text-silver-400'
    'hover:text-slate-900' = 'hover:text-onyx-800'
    'hover:text-slate-800' = 'hover:text-onyx-700'
    'placeholder-slate-400' = 'placeholder-silver-400'
    'border-slate-200' = 'border-silver-200'
    'border-slate-300' = 'border-silver-300'
    'hover:border-slate-300' = 'hover:border-silver-400'
    'divide-slate-100' = 'divide-silver-100'
    'divide-slate-200' = 'divide-silver-200'
    'bg-slate-100' = 'bg-silver-100'
    'bg-slate-200' = 'bg-silver-200'
    'bg-slate-50' = 'bg-silver-50'
    'hover:bg-slate-50' = 'hover:bg-silver-50'
    'hover:bg-slate-100' = 'hover:bg-silver-100'
    'hover:bg-slate-200' = 'hover:bg-silver-200'
}

foreach ($f in $files) {
    $c = Get-Content $f -Raw
    foreach ($k in $map.Keys) {
        $c = $c.Replace($k, $map[$k])
    }
    Set-Content -Path $f -Value $c -NoNewline
    Write-Output "updated $f"
}
