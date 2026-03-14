// qml/ScoreArea.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import RinUI

Pane {
    id: root

    property alias bridge: rowLayout.bridge

    background: Rectangle {
        color: Theme.currentTheme ? Theme.currentTheme.colors.cardColor : "lightgray"
        // 仅上下边线，作为区块分隔
        Rectangle {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            height: 1
            color: Theme.currentTheme ? Theme.currentTheme.colors.dividerBorderColor : "#e0e0e0"
        }
        Rectangle {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: 1
            color: Theme.currentTheme ? Theme.currentTheme.colors.dividerBorderColor : "#e0e0e0"
        }
    }

    RowLayout {
        id: rowLayout
        anchors.fill: parent
        anchors.leftMargin: 20
        anchors.rightMargin: 20

        property var bridge: null

        AppText {
            id: totalTime
            text: "时间: " + (rowLayout.bridge ? rowLayout.bridge.totalTime.toFixed(1) : "0.0")
        }
        AppText {
            id: typeSpeed
            text: "速度: " + (rowLayout.bridge ? rowLayout.bridge.typeSpeed.toFixed(2) : "0.00")
        }
        AppText {
            id: keyStroke
            text: "击键: " + (rowLayout.bridge ? rowLayout.bridge.keyStroke.toFixed(2) : "0.00")
        }
        AppText {
            id: codeLength
            text: "码长: " + (rowLayout.bridge ? rowLayout.bridge.codeLength.toFixed(2) : "0.00")
        }
        AppText {
            id: charNum
            text: "字数: " + (rowLayout.bridge ? rowLayout.bridge.charNum : 0)
        }
    }
}
