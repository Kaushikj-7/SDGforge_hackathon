# Medical Fact Verifier Browser Extension

A Chrome/Edge browser extension that integrates with your Python backend for AI-powered medical fact verification using the Llama 3 70B 8192 model.

## Features

### ✨ Core Functionality

- **Context Menu Trigger**: Right-click on highlighted text and select "Verify Medical Fact"
- **AI-Powered Verification**: Uses Llama 3 70B 8192 model for medical fact checking
- **Color-Coded Banners**: Visual indicators for fact verification results
  - 🟢 Green: Safe information
  - 🟡 Yellow: Use caution
  - 🔴 Red: Harmful misinformation
- **Detailed Information Panel**: Hover/click for explanations and trusted sources
- **Dashboard Analytics**: Track verification statistics and flagged domains

### 🎨 User Interface

- Clean, modern design with light/dark theme support
- Responsive layout that works on all screen sizes
- Non-intrusive banners that don't disrupt browsing
- Interactive charts showing verification statistics

## Installation

### For Development (Load Unpacked)

1. **Download/Clone** this extension to your local machine
2. **Open Chrome/Edge** and navigate to extensions page:
   - Chrome: `chrome://extensions/`
   - Edge: `edge://extensions/`
3. **Enable Developer Mode** (toggle in top-right corner)
4. **Click "Load unpacked"** and select the extension folder
5. **Configure Backend URL** in `background.js` (line 8):
   ```javascript
   const API_BASE_URL = "http://localhost:5000/api"; // Your backend URL
   ```

### Backend Integration

Your Python backend should expose an endpoint:

```
POST /api/verify
Content-Type: application/json

Request Body:
{
  "text": "<selected_text>",
  "source_url": "<page_url>",
  "model": "llama3-70b-8192"
}

Response:
{
  "status": "safe" | "caution" | "harmful",
  "corrected_fact": "Corrected information...",
  "explanation": "Detailed explanation...",
  "source_links": ["https://who.int", "https://cdc.gov"]
}
```

## File Structure

```
browser-extension/
├── manifest.json          # Extension configuration
├── background.js          # Service worker for API calls
├── content.js            # Content script for DOM manipulation
├── content.css           # Styles for injected banners
├── popup.html            # Dashboard popup HTML
├── popup.js              # Dashboard functionality
├── popup.css             # Dashboard styles
├── icons/                # Extension icons (16x16 to 128x128)
└── README.md             # This file
```

## Usage

1. **Highlight any medical text** on any webpage
2. **Right-click** and select "Verify Medical Fact"
3. **View the color-coded banner** that appears:
   - Click the info button (ⓘ) for detailed explanation
   - Click the X to close the banner
4. **Open the dashboard** by clicking the extension icon to see:
   - Session statistics
   - Pie chart of verification results
   - List of flagged domains
   - Export/clear data options

## Technical Details

### Manifest V3 Compliance

- Uses service worker instead of background pages
- Implements proper permissions model
- Follows Chrome Web Store guidelines

### Permissions Used

- `contextMenus`: Create right-click menu options
- `activeTab`: Access current tab content
- `scripting`: Inject content scripts
- `storage`: Save session data and preferences

### API Integration

- Automatic retry logic for failed requests
- Timeout handling (30 seconds)
- Error fallback with user-friendly messages
- Real-time statistics tracking

## Customization

### Changing Backend URL

Edit `background.js` line 8:

```javascript
const API_BASE_URL = "https://your-backend.com/api";
```

### Modifying Banner Styles

Edit `content.css` to customize:

- Colors and gradients
- Animation effects
- Responsive breakpoints
- Dark theme support

### Adding New Features

- Banner types: Modify `content.js` createBanner() function
- Dashboard widgets: Add sections to `popup.html`
- Storage: Use `chrome.storage.local` API for persistence

## Troubleshooting

### Common Issues

**Banner not appearing:**

- Check if text is properly highlighted
- Verify backend API is running and accessible
- Check browser console for errors

**API connection failed:**

- Ensure backend URL is correct in `background.js`
- Check CORS settings on your backend
- Verify API endpoint responds with correct JSON format

**Dashboard not updating:**

- Extension uses real-time storage updates
- Try closing and reopening the popup
- Check if storage permissions are granted

### Debug Mode

Enable debug logging by adding to `background.js`:

```javascript
console.log("Debug: API request sent", requestData);
```

## Browser Compatibility

- ✅ Chrome 88+
- ✅ Edge 88+
- ✅ Chromium-based browsers
- ❌ Firefox (requires Manifest V2 conversion)
- ❌ Safari (requires different API)

## Privacy & Security

- **No data collection**: All data stays local to your browser
- **Secure communications**: Only HTTPS endpoints supported in production
- **Minimal permissions**: Only requests necessary permissions
- **Open source**: All code is readable and auditable

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with different websites
5. Submit a pull request

## License

MIT License - Feel free to modify and distribute.

---

**Powered by Llama 3 70B 8192 🤖**
