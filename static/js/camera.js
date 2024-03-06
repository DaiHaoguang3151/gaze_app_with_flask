// 打开摄像头
async function openCamera(video) {
    try {
        globalStream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = globalStream;
    } catch (error) {
        console.error('Error occurred while opening the camera:', error);
    }
}


// 截取视频帧
async function captureFrame(imageCapture, canvas_cap, ctx_cap) {
    // 这边是将截图显式在页面上
    const imgBitmap = await imageCapture.grabFrame();
    canvas_cap.width = imgBitmap.width;
    canvas_cap.height = imgBitmap.height;
    ctx_cap.drawImage(imgBitmap, 0, 0);

    // 这是新创建了一个不显示的canvas，用于截取视频帧，并传给后端
    const canvas = document.createElement('canvas');
    canvas.width = imgBitmap.width;
    canvas.height = imgBitmap.height;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(imgBitmap, 0, 0);
    // 返回blob对象
    return new Promise((resolve, reject) => {
        canvas.toBlob(blob => {
            if (blob) {
                resolve(blob);
            } else {
                reject(new Error('Failed to create blob'));
            }
        }, 'image/jpeg');
    });
}


// Blob转换成base64
function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(blob);
    });
}