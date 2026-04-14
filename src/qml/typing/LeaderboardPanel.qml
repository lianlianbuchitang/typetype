import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import RinUI

Frame {
    id: root
    radius: 0
    hoverable: false
    color: Theme.currentTheme.colors.cardColor

    property var currentTextInfo: null
    property var leaderboardRecords: []
    property int textId: 0

    signal closeRequested

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Header
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 44
            color: Theme.currentTheme.colors.subtleColor

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 12
                anchors.rightMargin: 8
                spacing: 8

                IconWidget {
                    Layout.preferredWidth: 20
                    Layout.preferredHeight: 20
                    Layout.alignment: Qt.AlignVCenter
                    icon: "ic_fluent_trophy_20_filled"
                    color: Theme.currentTheme.colors.primaryColor
                }

                Text {
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignVCenter
                    typography: Typography.BodyStrong
                    text: currentTextInfo ? currentTextInfo.title : qsTr("排行榜")
                    elide: Text.ElideRight
                }

                Button {
                    Layout.preferredWidth: 28
                    Layout.preferredHeight: 28
                    flat: true
                    enabled: appBridge ? !appBridge.leaderboardLoading : true
                    onClicked: {
                        if (appBridge && root.textId > 0) {
                            appBridge.loadLeaderboardByTextId(root.textId);
                        }
                    }
                    contentItem: IconWidget {
                        icon: "ic_fluent_arrow_sync_20_regular"
                        size: 14
                        color: Theme.currentTheme.colors.textSecondaryColor
                    }
                }

                Button {
                    Layout.preferredWidth: 28
                    Layout.preferredHeight: 28
                    text: "✕"
                    flat: true
                    onClicked: root.closeRequested()
                }
            }
        }

        // Separator
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 1
            color: Theme.currentTheme.colors.cardBorderColor
        }

        // My rank card (visible when logged in and has data)
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 56
            visible: appBridge && appBridge.loggedin && leaderboardRecords.length > 0
            color: Theme.currentTheme.colors.subtleSecondaryColor

            ColumnLayout {
                anchors.fill: parent
                anchors.leftMargin: 12
                anchors.rightMargin: 12
                anchors.topMargin: 8
                anchors.bottomMargin: 8
                spacing: 2

                Text {
                    typography: Typography.Caption
                    color: Theme.currentTheme.colors.textSecondaryColor
                    text: qsTr("我的排名")
                }

                Text {
                    typography: Typography.BodyStrong
                    color: Theme.currentTheme.colors.primaryColor
                    text: {
                        if (!appBridge || !appBridge.loggedin) return "--";
                        var nick = appBridge.userNickname || appBridge.currentUser || "";
                        for (var i = 0; i < leaderboardRecords.length; i++) {
                            var r = leaderboardRecords[i];
                            if ((r.nickname || r.username || "") === nick) {
                                return "#" + r.rank + "  " + Number(r.speed).toFixed(1);
                            }
                        }
                        return "--";
                    }
                }
            }
        }

        // My rank separator
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 1
            visible: appBridge && appBridge.loggedin && leaderboardRecords.length > 0
            color: Theme.currentTheme.colors.cardBorderColor
        }

        // Table header
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 32
            color: Theme.currentTheme.colors.subtleColor
            visible: leaderboardRecords.length > 0

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 8
                anchors.rightMargin: 8
                spacing: 4

                Text {
                    Layout.preferredWidth: 32
                    typography: Typography.Caption
                    font.weight: Font.DemiBold
                    horizontalAlignment: Text.AlignHCenter
                    text: qsTr("名次")
                }

                Text {
                    Layout.fillWidth: true
                    typography: Typography.Caption
                    font.weight: Font.DemiBold
                    text: qsTr("用户")
                }

                Text {
                    Layout.preferredWidth: 60
                    typography: Typography.Caption
                    font.weight: Font.DemiBold
                    horizontalAlignment: Text.AlignRight
                    text: qsTr("速度")
                }
            }
        }

        // Table header separator
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 1
            visible: leaderboardRecords.length > 0
            color: Theme.currentTheme.colors.cardBorderColor
        }

        // Loading indicator
        BusyIndicator {
            Layout.alignment: Qt.AlignCenter
            Layout.topMargin: 40
            Layout.preferredWidth: 32
            Layout.preferredHeight: 32
            visible: appBridge && appBridge.leaderboardLoading
        }

        // "本地文本" message
        Text {
            Layout.alignment: Qt.AlignHCenter
            Layout.topMargin: 60
            Layout.leftMargin: 20
            Layout.rightMargin: 20
            typography: Typography.Body
            color: Theme.currentTheme.colors.textSecondaryColor
            text: qsTr("本地文本不参与排行")
            visible: root.textId === 0
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
        }

        // "暂无数据" message
        Text {
            Layout.alignment: Qt.AlignHCenter
            Layout.topMargin: 60
            Layout.leftMargin: 20
            Layout.rightMargin: 20
            typography: Typography.Body
            color: Theme.currentTheme.colors.textSecondaryColor
            text: qsTr("暂无排行数据")
            visible: root.textId > 0 && leaderboardRecords.length === 0 && !(appBridge && appBridge.leaderboardLoading)
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
        }

        // Leaderboard list
        ListView {
            id: lbListView
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: leaderboardRecords
            visible: leaderboardRecords.length > 0

            delegate: Rectangle {
                width: lbListView.width
                height: 36
                color: index % 2 === 0 ? "transparent" : Theme.currentTheme.colors.subtleColor

                property bool hovered: lbMouseArea.containsMouse
                onHoveredChanged: {
                    color = hovered ? Theme.currentTheme.colors.subtleSecondaryColor :
                        (index % 2 === 0 ? "transparent" : Theme.currentTheme.colors.subtleColor);
                }

                MouseArea {
                    id: lbMouseArea
                    anchors.fill: parent
                    hoverEnabled: true
                    acceptedButtons: Qt.NoButton
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 8
                    anchors.rightMargin: 8
                    spacing: 4

                    // Rank with trophy
                    Rectangle {
                        Layout.preferredWidth: 32
                        Layout.fillHeight: true
                        color: "transparent"

                        Row {
                            anchors.centerIn: parent
                            spacing: 1

                            IconWidget {
                                anchors.verticalCenter: parent.verticalCenter
                                width: 12
                                height: 12
                                visible: modelData.rank <= 3
                                icon: "ic_fluent_trophy_20_filled"
                                color: modelData.rank === 1 ? "#FFD700" :
                                       modelData.rank === 2 ? "#C0C0C0" :
                                       "#CD7F32"
                            }

                            Text {
                                anchors.verticalCenter: parent.verticalCenter
                                typography: Typography.Caption
                                font.weight: Font.DemiBold
                                color: {
                                    if (modelData.rank === 1) return "#FFD700";
                                    if (modelData.rank === 2) return "#C0C0C0";
                                    if (modelData.rank === 3) return "#CD7F32";
                                    return Theme.currentTheme.colors.textColor;
                                }
                                text: modelData.rank
                            }
                        }
                    }

                    // Name
                    Text {
                        Layout.fillWidth: true
                        typography: Typography.Caption
                        text: modelData.nickname || modelData.username || qsTr("匿名")
                        elide: Text.ElideRight
                    }

                    // Speed
                    Text {
                        Layout.preferredWidth: 60
                        typography: Typography.Caption
                        font.weight: Font.DemiBold
                        color: Theme.currentTheme.colors.primaryColor
                        horizontalAlignment: Text.AlignRight
                        text: modelData.speed ? Number(modelData.speed).toFixed(1) : "-"
                    }
                }
            }

            ScrollBar.vertical: ScrollBar {
                policy: ScrollBar.AsNeeded
            }
        }

        // Spacer
        Item { Layout.fillHeight: true }
    }

    // Listen for leaderboard updates
    Connections {
        target: appBridge

        function onLeaderboardLoaded(data) {
            root.leaderboardRecords = data.leaderboard || [];
            root.currentTextInfo = data.text_info;
        }

        function onLeaderboardLoadFailed(message) {
            root.leaderboardRecords = [];
        }
    }
}
