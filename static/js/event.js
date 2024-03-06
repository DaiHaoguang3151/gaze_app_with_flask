// 为元素添加事件监听，执行相关动作
function addEventListener(elementId, event, actionFunction) {
    // elementId: 元素id event: 监听的事件 actionFunction: 需要执行的动作
    const element = document.getElementById(elementId);
    if (element) {
        element.addEventListener(event, () => {
            actionFunction(elementId)
        });
    } else {
        console.error(`Element with ID ${elementId} not found`);
    }
};