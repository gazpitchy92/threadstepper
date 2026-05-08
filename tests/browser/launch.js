const { app, BrowserWindow, session } = require('electron')

app.commandLine.appendSwitch('disable-cache')

app.whenReady().then(async () => {
    await session.defaultSession.clearCache()

    const win = new BrowserWindow({ show: true })

    win.webContents.session.webRequest.onBeforeSendHeaders((details, callback) => {
        details.requestHeaders['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        details.requestHeaders['Pragma'] = 'no-cache'
        callback({ requestHeaders: details.requestHeaders })
    })

    const filePath = process.argv[2]
    await win.loadFile(filePath)
    win.webContents.reloadIgnoringCache()
})