import QtQuick.Controls
import RinUI

Dialog {
    id: root
    property var bridge: null
    property string scoreMessage: ""

    modal: true
    title: "打字结束"
    standardButtons: Dialog.Ok | Dialog.Cancel

    AppText {
        text: "<b>本次跟打结束，是否复制成绩？</b><br>" + root.scoreMessage
        color: Theme.currentTheme ? Theme.currentTheme.colors.textColor : "#2c3e50"
        leftPadding: 20
        rightPadding: 20
    }

    function copyScoreMessage() {
        if (!root.bridge) {
            return;
        }
        root.bridge.copyScoreMessage();
    }

    onAccepted: {
        copyScoreMessage();
        console.log("Ok clicked");
    }
    onRejected: console.log("Cancel clicked")
}
