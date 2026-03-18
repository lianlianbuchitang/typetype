import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import RinUI

FluentPage {
    title: qsTr("个人中心")

    // 个人信息卡片（登录后显示）
    Frame {
        id: profileCard
        //Layout.alignment: Qt.AlignCenter
        Layout.preferredWidth: 280
        Layout.preferredHeight: 160
        radius: 10
        visible: appBridge ? appBridge.loggedin : false

        ColumnLayout {
            anchors.fill: parent
            spacing: 12

            RowLayout {
                Layout.fillWidth: true
                spacing: 16

                Image {
                    id: profilePicture
                    source: resourceBaseUrl + "images/TypeTypeLogo.png"
                    Layout.preferredWidth: 64
                    Layout.preferredHeight: 64
                    fillMode: Image.PreserveAspectFit
                }

                ColumnLayout {
                    Layout.preferredWidth: profilePicture.width
                    Layout.preferredHeight: profilePicture.height

                    Text {
                        id: nickname
                        typography: Typography.BodyStrong
                        text: appBridge ? (appBridge.userNickname || qsTr("昵称")) : qsTr("昵称")
                    }
                    Text {
                        id: username
                        typography: Typography.Caption
                        color: Theme.currentTheme.colors.textSecondaryColor
                        text: appBridge ? (appBridge.currentUser || qsTr("用户名")) : qsTr("用户名")
                    }
                }
            }

            Button {
                Layout.fillWidth: true
                text: qsTr("退出登录")
                onClicked: {
                    if (appBridge)
                        appBridge.logout();
                }
            }
        }
    }

    // 登录按钮（未登录时显示）
    Button {
        id: loginButton
        Layout.alignment: Qt.AlignCenter
        text: qsTr("登录")
        highlighted: true
        visible: appBridge ? !appBridge.loggedin : true
        onClicked: {
            loginDialog.open();
        }
    }

    Dialog {
        id: loginDialog
        title: qsTr("登录")
        modal: true

        ColumnLayout {
            width: 300
            spacing: 12

            TextField {
                id: usernameField
                placeholderText: qsTr("用户名")
                Layout.fillWidth: true
            }

            TextField {
                id: passwordField
                placeholderText: qsTr("密码")
                echoMode: TextInput.Password
                Layout.fillWidth: true
            }

            Text {
                id: errorText
                visible: false
                color: Theme.currentTheme.colors.systemCriticalColor
                typography: Typography.Caption
                Layout.fillWidth: true
                horizontalAlignment: Qt.AlignCenter
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                Button {
                    text: qsTr("取消")
                    Layout.fillWidth: true
                    onClicked: loginDialog.close()
                }

                Button {
                    id: loginBtn
                    text: qsTr("登录")
                    highlighted: true
                    Layout.fillWidth: true
                    onClicked: {
                        const username = usernameField.text.trim();
                        const password = passwordField.text;
                        if (!username || !password) {
                            errorText.text = qsTr("请输入用户名和密码");
                            errorText.visible = true;
                            return;
                        }
                        errorText.visible = false;
                        loginBtn.enabled = false;
                        if (appBridge)
                            appBridge.login(username, password);
                    }
                }
            }
        }
    }

    Connections {
        target: appBridge
        enabled: appBridge !== null
        function onLoginResult(success, message) {
            loginBtn.enabled = true;
            if (success) {
                loginDialog.close();
            } else {
                errorText.text = message;
                errorText.visible = true;
            }
        }
    }
}
