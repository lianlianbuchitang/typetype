// qml/ToolLine.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import RinUI

Pane {
    id: root

    property var textSourceOptions: []
    property string defaultTextSourceKey: ""
    readonly property string currentSourceKey: sourceSelector.currentValue || ""

    signal requestLoadText(string sourceKey)
    signal requestLoadTextFromClipboard // 定义从剪贴板载文信号
    signal requestRetype
    signal requestToggleLeaderboard

    // 将 JS 数组转换为 ListModel，使 RinUI ContextMenu 能正确按 textRole 读取
    ListModel {
        id: sourceListModel
    }

    onTextSourceOptionsChanged: {
        sourceListModel.clear();
        for (var i = 0; i < textSourceOptions.length; i++) {
            sourceListModel.append(textSourceOptions[i]);
        }
        // 恢复默认选中项
        if (defaultTextSourceKey) {
            for (var j = 0; j < sourceListModel.count; j++) {
                if (sourceListModel.get(j).key === defaultTextSourceKey) {
                    sourceSelector.currentIndex = j;
                    break;
                }
            }
        }
    }

    // 自定义 Pane 的背景（跟随 RinUI 主题）
    background: Rectangle {
        color: Theme.currentTheme ? Theme.currentTheme.colors.cardColor : "#d3d3d3"
        radius: 2
        border.color: Theme.currentTheme ? Theme.currentTheme.colors.controlBorderColor : "#b0b0b0"
        border.width: 1
    }

    RowLayout {
        id: rowLayout
        anchors.fill: parent
        anchors.leftMargin: 15
        anchors.rightMargin: 15
        spacing: 15

        Image {
            source: resourceBaseUrl + "images/TypeTypeLogo.png"
            Layout.preferredHeight: 60
            Layout.alignment: Qt.AlignVCenter
            fillMode: Image.PreserveAspectFit   // 保持宽高比，不会变形
        }

        ComboBox {
            id: sourceSelector
            Layout.preferredWidth: 140
            Layout.preferredHeight: 40
            Layout.alignment: Qt.AlignVCenter
            model: sourceListModel
            textRole: "label"
            valueRole: "key"
        }

        Button {
            id: loadText
            Layout.preferredWidth: 140
            Layout.preferredHeight: 40
            Layout.alignment: Qt.AlignVCenter
            text: "载文"
            onClicked: {
                root.requestLoadText(sourceSelector.currentValue || root.defaultTextSourceKey);
            }
        }

        Button {
            id: clipboardLoadText
            Layout.preferredWidth: 140
            Layout.preferredHeight: 40
            Layout.alignment: Qt.AlignVCenter
            text: "剪贴板载文"
            onClicked: {
                root.requestLoadTextFromClipboard();
            }
        }

        Button {
            id: retype
            Layout.preferredWidth: 140
            Layout.preferredHeight: 40
            Layout.alignment: Qt.AlignVCenter
            text: "重打[F3]"
            onClicked: {
                root.requestRetype();
            }
        }

        // Spacer to push leaderboard button to the right
        Item { Layout.fillWidth: true }

        // 排行榜切换按钮
        Button {
            id: leaderboardToggle
            Layout.preferredWidth: 40
            Layout.preferredHeight: 40
            Layout.alignment: Qt.AlignVCenter
            text: "🏆"
            onClicked: {
                root.requestToggleLeaderboard();
            }

            ToolTip {
                text: qsTr("排行榜")
                parent: parent
                visible: parent.hovered
            }
        }
    }
}
