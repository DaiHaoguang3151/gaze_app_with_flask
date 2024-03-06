function drawLine(startPt, endPt, strokeStyle='#00FF00') {
    // 绘制直线
    ctx_cap.strokeStyle = strokeStyle; // 设置颜色为绿色
    ctx_cap.lineWidth = 2; // 设置线条宽度
    ctx_cap.beginPath();
    ctx_cap.moveTo(startPt[0], startPt[1]); // 设置起始点
    ctx_cap.lineTo(endPt[0], endPt[1]); // 设置终点
    ctx_cap.stroke(); // 绘制线段
}


function drawBox(box) {
    for (let i = 0; i < box.length; i++) {
        startPt = box[i];
        endPt = box[(i + 1) % box.length];
        drawLine(startPt, endPt);
    }
}