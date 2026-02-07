# Zing MP3 Player Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2025.10%2B-blue.svg)](https://www.home-assistant.io/)

Tích hợp Zing MP3 cho Home Assistant, cho phép bạn tìm kiếm và phát nhạc từ Zing MP3 trên các media player trong Home Assistant như Chromecast, Sonos, v.v.

## 📋 Mục lục

- [Tính năng](#-tính-năng)
- [Yêu cầu](#-yêu-cầu)
- [Cài đặt](#-cài-đặt)
- [Cấu hình](#-cấu-hình)
- [Sử dụng](#-sử-dụng)
- [Services](#-services)
- [Entities](#-entities)
- [Troubleshooting](#-troubleshooting)
- [Changelog](#-changelog)

## ✨ Tính năng

- 🔍 **Tìm kiếm nhạc**: Tìm kiếm bài hát, playlist, ca sĩ, album trên Zing MP3
- ▶️ **Phát nhạc**: Phát nhạc từ Zing MP3 trên bất kỳ media player nào trong Home Assistant
- 📱 **Media Browser**: Duyệt và chọn nhạc trực tiếp từ giao diện Home Assistant
- 🔄 **Auto-play**: Tự động phát bài tiếp theo trong playlist/album
- 🎚️ **Điều khiển đầy đủ**: Play, pause, stop, next, previous, shuffle, repeat
- 🔊 **Chọn speaker**: Chuyển đổi giữa các speaker khác nhau
- 📊 **Sensor**: Theo dõi thông tin bài hát đang phát, danh sách bài hát, kết quả tìm kiếm
- 🎯 **Select entities**: Dropdown để chọn speaker, play mode, repeat mode
- 🤖 **LLM Integration**: Hỗ trợ tích hợp với LLM/AI để điều khiển bằng giọng nói

## 🔧 Yêu cầu

- **Home Assistant**: >= 2025.10.0
- **Media Player**: Ít nhất một media player trong Home Assistant (Chromecast, Sonos, v.v.)

## 📦 Cài đặt

### Bước 1: Cài đặt Media Card (Bắt buộc)

Media card cung cấp giao diện để duyệt và chọn nhạc từ Zing MP3. **Bạn phải cài đặt media card trước khi cài đặt integration.**

#### Cách 1: Cài đặt thủ công (Khuyến nghị)

1. Tải file `zingmp3-media-card.js` từ repository này
2. Tạo thư mục `www` trong thư mục cấu hình Home Assistant (nếu chưa có)
3. Sao chép file `zingmp3-media-card.js` vào `www/zingmp3-media-card.js`
4. Thêm qua UI: **Settings** → **Dashboards** → **Resources** → **Add Resource**
   - URL: `/local/zingmp3-media-card.js`
   - Resource type: `JavaScript Module`
5. Restart Home Assistant

### Bước 2: Cài đặt Integration

#### Cách 1: Cài đặt qua HACS (Khuyến nghị)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=smarthomeblack&repository=zingmp3_player&category=integration)

- Tải về sau đó khởi động lại Home Assistant

#### Cách 2: Cài đặt thủ công

Nếu không sử dụng HACS, bạn có thể cài đặt thủ công như sau:

1. Tải mã nguồn repo này về máy
2. Sao chép thư mục `custom_components/zingmp3_player` vào thư mục `custom_components` trong thư mục cấu hình Home Assistant của bạn
3. Khởi động lại Home Assistant
4. Vào **Settings** → **Devices & Services** → **Add Integration** → Tìm và chọn **Zing MP3 Player** và cấu hình theo hướng dẫn

## ⚙️ Cấu hình

### Cấu hình qua UI (Config Flow)

1. Vào **Settings** → **Devices & Services**
2. Nhấn **Add Integration**
3. Tìm và chọn **Zing MP3 Player**
4. Điền các thông tin:
   - **Name**: Tên cho tích hợp (mặc định: `zingmp3_player`)
   - **Speakers**: Danh sách media players để phát nhạc (tùy chọn, có thể cấu hình sau)
   - **Extra Sensor**: Bật/tắt sensor để theo dõi thông tin chi tiết
   - **Dropdowns**: Chọn các dropdown entities cần tạo (speakers, playmode, repeatmode)

5. Nhấn **Submit** để hoàn tất

### Cấu hình qua YAML (Tùy chọn)

Bạn cũng có thể cấu hình một số tùy chọn trong `configuration.yaml`:

```yaml
zingmp3_player:
  name: zingmp3_player
  speakers: media_player.chromecast, media_player.sonos
  extra_sensor: true
  dropdowns:
    - speakers
    - playmode
    - repeatmode
```

## 🎮 Sử dụng

### Thêm Media Card vào Dashboard

Sau khi cài đặt media card, bạn có thể thêm card vào Lovelace dashboard:

1. Vào **Settings** → **Dashboards** → Chọn dashboard của bạn
2. Nhấn **⋮** (menu) → **Edit Dashboard**
3. Nhấn **+ Add Card** → **Manual** (hoặc **By Card**)
4. Thêm cấu hình sau:

```yaml
type: custom:zingmp3-playing-card
entity_id: media_player.zingmp3_player
header: Zing MP3 Music
```

**Các tùy chọn:**
- `entity_id`: Entity ID của Zing MP3 Player (mặc định: `media_player.zingmp3_player`)
- `header`: Tiêu đề hiển thị trên card (tùy chọn)

### Media Browser

1. Vào bất kỳ media player card nào trong Home Assistant
2. Nhấn vào nút **Browse Media** (biểu tượng thư mục)
3. Chọn **Zing MP3 Player** từ danh sách
4. Duyệt và chọn:
   - **Search**: Tìm kiếm bài hát, playlist, ca sĩ
   - **PLAYING**: Xem danh sách bài hát đang phát
   - **Playlists**: Duyệt playlist (nếu có)

### Services

#### `zingmp3_player.search`

Tìm kiếm nhạc trên Zing MP3.

```yaml
service: zingmp3_player.search
target:
  entity_id: media_player.zingmp3_player
data:
  query: "Sơn Tùng M-TP"
  filter: "songs"  # hoặc "playlists"
  limit: 20
```

**Parameters:**
- `query` (required): Từ khóa tìm kiếm
- `filter` (optional): Loại kết quả - `songs` hoặc `playlists` (mặc định: `songs`)
- `limit` (optional): Số lượng kết quả (1-20, mặc định: 20)

**Kết quả:** Được lưu trong `sensor.zingmp3_player_extra` với attribute `search`

#### `zingmp3_player.call_method`

Gọi các method tùy chỉnh của media player.

```yaml
service: zingmp3_player.call_method
target:
  entity_id: media_player.zingmp3_player
data:
  command: "goto_track"
  parameters:
    track_no: 5
```

**Parameters:**
- `command` (required): Tên command (ví dụ: `goto_track`)
- `parameters` (optional): Tham số cho command (dict)

### Media Player Controls

Sử dụng các service chuẩn của Home Assistant:

- `media_player.play_media`: Phát nhạc
  ```yaml
  service: media_player.play_media
  target:
    entity_id: media_player.zingmp3_player
  data:
    media_content_id: "ZW69BZOF"  # ID bài hát
    media_content_type: "music"   # hoặc "playlist"
  ```

- `media_player.media_play`: Tiếp tục phát
- `media_player.media_pause`: Tạm dừng
- `media_player.media_stop`: Dừng
- `media_player.media_next_track`: Bài tiếp theo
- `media_player.media_previous_track`: Bài trước
- `media_player.select_source`: Chọn speaker
- `media_player.shuffle_set`: Bật/tắt shuffle
- `media_player.repeat_set`: Đặt repeat mode (`off`, `one`, `all`)

## 📊 Entities

### Media Player

**Entity ID**: `media_player.zingmp3_player`

**States:**
- `playing`: Đang phát
- `paused`: Tạm dừng
- `idle`: Không phát
- `off`: Tắt

**Attributes:**
- `media_title`: Tên bài hát
- `media_artist`: Tên ca sĩ
- `media_album_name`: Tên album
- `media_image_url`: URL ảnh bìa
- `media_duration`: Thời lượng (giây)
- `media_position`: Vị trí hiện tại (giây)
- `shuffle`: Trạng thái shuffle (true/false)
- `repeat`: Repeat mode (off/one/all)
- `source`: Speaker đang sử dụng
- `source_list`: Danh sách speakers có sẵn

### Sensor (Optional)

**Entity ID**: `sensor.zingmp3_player_extra`

**Attributes:**
- `search`: Danh sách kết quả tìm kiếm (JSON array)
- `tracks`: Danh sách bài hát đang phát (JSON array)
- `total_tracks`: Tổng số bài hát trong playlist/album

**Cấu trúc kết quả tìm kiếm:**
```json
[
  {
    "media_content_id": "ZW69BZOF",
    "media_content_type": "songs",
    "title": "Tên bài hát",
    "artist": "Tên ca sĩ",
    "albumName": "Tên album",
    "images": "URL ảnh bìa"
  }
]
```

### Select Entities (Optional)

- `select.zingmp3_player_speakers`: Chọn speaker
- `select.zingmp3_player_playmode`: Chọn play mode (nếu có)
- `select.zingmp3_player_repeatmode`: Chọn repeat mode

## 🔍 Troubleshooting

### Lỗi: Integration không xuất hiện trong danh sách

- Đảm bảo đã restart Home Assistant sau khi cài đặt
- Kiểm tra file `manifest.json` có đúng format không
- Kiểm tra logs trong Home Assistant để xem lỗi chi tiết

### Lỗi: Không tìm thấy nhạc

- Kiểm tra kết nối internet
- Kiểm tra từ khóa tìm kiếm có đúng không
- Thử tìm kiếm với từ khóa khác
- Kiểm tra logs: `home-assistant.log` hoặc Developer Tools → Logs

### Lỗi: Nhạc không phát

- Kiểm tra speaker (source) đã được chọn chưa
- Kiểm tra speaker có đang hoạt động không
- Kiểm tra `media_player.zingmp3_player` không được chọn làm speaker (tránh recursion)
- Kiểm tra stream URL có hợp lệ không trong logs

### Lỗi: Sensor không cập nhật

- Đảm bảo đã bật **Extra Sensor** trong cấu hình
- Kiểm tra entity `sensor.zingmp3_player_extra` có tồn tại không
- Restart Home Assistant

### Debug Mode

Để bật debug logging, thêm vào `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.zingmp3_player: debug
```

Sau đó restart Home Assistant và kiểm tra logs.

---

## 📸 Demo

<img title="Zing MP3 Player" src="https://raw.githubusercontent.com/smarthomeblack/zingmp3_player/refs/heads/main/1.png" width="100%"></img>

<img title="Zing MP3 Player" src="https://raw.githubusercontent.com/smarthomeblack/zingmp3_player/refs/heads/main/2.png" width="100%"></img>

<img title="Zing MP3 Player" src="https://raw.githubusercontent.com/smarthomeblack/zingmp3_player/refs/heads/main/3.png" width="100%"></img>

<img title="Zing MP3 Player" src="https://raw.githubusercontent.com/smarthomeblack/zingmp3_player/refs/heads/main/4.png" width="100%"></img>

<img title="Zing MP3 Player" src="https://raw.githubusercontent.com/smarthomeblack/zingmp3_player/refs/heads/main/5.png" width="100%"></img>

---

## 📝 Changelog

### Version 2026.2.8

**Initial Release**
- ✅ Tích hợp Zing MP3 với Home Assistant
- ✅ Media Browser để duyệt và chọn nhạc
- ✅ Tìm kiếm bài hát, playlist, ca sĩ, album
- ✅ Phát nhạc trên media player (Chromecast, Sonos, v.v.)
- ✅ Auto-play playlist/album
- ✅ Điều khiển đầy đủ: play, pause, stop, next, previous
- ✅ Shuffle và repeat
- ✅ Chọn speaker
- ✅ Optional sensor để theo dõi thông tin chi tiết
- ✅ Optional select entities cho speakers, play mode, repeat mode
- ✅ Service `search` để tìm kiếm nhạc
- ✅ Service `call_method` để gọi các method tùy chỉnh
- ✅ Hỗ trợ LLM/AI integration
- ✅ Config flow UI

## 🤝 Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng:

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/ten-tinh-nang`)
3. Commit changes (`git commit -m 'Thêm tính năng mới'`)
4. Push to branch (`git push origin feature/ten-tinh-nang`)
5. Mở Pull Request

**Ví dụ:**
- `feature/fix-search-bug` - Sửa lỗi tìm kiếm
- `feature/add-playlist-support` - Thêm hỗ trợ playlist
- `feature/improve-error-handling` - Cải thiện xử lý lỗi

## 📄 License

MIT License - xem file [LICENSE](LICENSE) để biết thêm chi tiết.

## 🙏 Credits

- **Author**: smarthomeblack
- **Inspired by**: yTube Music Player integration
- **Zing MP3 API**: Zing MP3

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/smarthomeblack/zingmp3_player/issues)
- **Discussions**: [GitHub Discussions](https://github.com/smarthomeblack/zingmp3_player/discussions)

---

**Lưu ý**: Tích hợp này không chính thức và không được Zing MP3 hỗ trợ. Sử dụng có trách nhiệm và tuân thủ các điều khoản sử dụng của Zing MP3.
