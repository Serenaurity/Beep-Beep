# 🚨 Campus Alert App

แอปพลิเคชันแจ้งเตือนภัยพิบัติและเหตุอันตรายภายในรั้วมหาวิทยาลัย

## 🚀 Quick Start

### เริ่มต้นใช้งาน
```powershell
# แก้ไข .env
notepad .env

# เริ่ม services
docker-compose up -d

# ดู logs
docker-compose logs -f

# หยุด services
docker-compose down
```

## 📡 API Endpoints

- GET  http://localhost/api/health
- GET  http://localhost/api/alerts
- POST http://localhost/api/alerts
- GET  http://localhost/api/messages

## 🔧 Useful Commands
```powershell
docker-compose ps                    # ดูสถานะ
docker-compose logs -f backend       # ดู backend logs
docker-compose restart               # รีสตาร์ท
docker-compose down -v               # ลบทั้งหมดรวม volumes
```
