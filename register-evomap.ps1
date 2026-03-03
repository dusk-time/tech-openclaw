# 🧬 EvoMap 节点注册脚本

$nodeId = "node_openclaw_$(Get-Random -Maximum 99999)"
$msgId = "msg_$([DateTimeOffset]::Now.ToUnixTimeSeconds())_$(Get-Random -Maximum 9999)"
$timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🧬 EvoMap 节点注册" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔑 节点 ID: $nodeId" -ForegroundColor Yellow
Write-Host "📅 时间：$timestamp" -ForegroundColor Yellow
Write-Host ""

$body = @{
    protocol = "gep-a2a"
    protocol_version = "1.0.0"
    message_type = "hello"
    message_id = $msgId
    sender_id = $nodeId
    timestamp = $timestamp
    payload = @{
        capabilities = @{
            type = "OpenClaw Agent"
            version = "1.0"
            skills = @("stock-analysis", "yahoo-finance", "web-search")
        }
        gene_count = 0
        capsule_count = 0
        env_fingerprint = @{
            platform = "win32"
            arch = "x64"
            node_version = "v22.14.0"
            openclaw = "true"
            workspace = "C:\Users\28054\.openclaw\workspace"
        }
    }
} | ConvertTo-Json -Depth 10

Write-Host "📤 正在发送到 EvoMap Hub..." -ForegroundColor Green
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri "https://evomap.ai/a2a/hello" -Method Post -ContentType "application/json" -Body $body -TimeoutSec 30
    
    Write-Host "✅ 注册成功！" -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "📊 响应信息" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    $response | ConvertTo-Json -Depth 10
    
    Write-Host ""
    Write-Host "💾 保存节点信息..." -ForegroundColor Yellow
    
    $nodeInfo = @{
        node_id = $nodeId
        hub_node_id = $response.hub_node_id
        your_node_id = $response.your_node_id
        claim_code = $response.claim_code
        claim_url = $response.claim_url
        registered_at = $timestamp
        status = "active"
        credits = 500
    }
    
    $nodeInfo | ConvertTo-Json -Depth 10 | Out-File -FilePath "evomap-node-info.json" -Encoding utf8
    
    Write-Host "✅ 节点信息已保存到：evomap-node-info.json" -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "🎉 下一步操作" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1️⃣ 访问 claim URL 绑定账户：" -ForegroundColor White
    Write-Host "   $($response.claim_url)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2️⃣ 你的节点 ID（永久身份）：" -ForegroundColor White
    Write-Host "   $nodeId" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "3️⃣ 获取 genesis-node-evomap 胶囊：" -ForegroundColor White
    Write-Host "   访问：https://evomap.ai/agent/genesis-node-evomap" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "4️⃣ 保持在线（每 15 分钟心跳）：" -ForegroundColor White
    Write-Host "   使用 Evolver 客户端或手动发送心跳" -ForegroundColor Cyan
    Write-Host ""
    
} catch {
    Write-Host "❌ 注册失败：$($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "可能原因:" -ForegroundColor Yellow
    Write-Host "  - 网络连接问题" -ForegroundColor White
    Write-Host "  - API 服务器暂时不可用" -ForegroundColor White
    Write-Host "  - 请求超时（请稍后重试）" -ForegroundColor White
    Write-Host ""
    Write-Host "建议:" -ForegroundColor Yellow
    Write-Host "  1. 检查网络连接" -ForegroundColor White
    Write-Host "  2. 稍后重试" -ForegroundColor White
    Write-Host "  3. 使用 Evolver 客户端：https://github.com/autogame-17/evolver" -ForegroundColor White
}

Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
