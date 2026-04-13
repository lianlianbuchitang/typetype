import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import RinUI

FluentPage {
    id: uploadPage
    title: qsTr("上传文本")

    property bool isCloud: false

    ListModel {
        id: sourceListModel
    }

    function reloadSourceList() {
        sourceListModel.clear();
        if (appBridge && appBridge.textSourceOptions) {
            for (var i = 0; i < appBridge.textSourceOptions.length; i++) {
                sourceListModel.append(appBridge.textSourceOptions[i]);
            }
        }
        sourceListModel.append({"key": "__custom__", "label": qsTr("自定义")});
    }

    function clearForm() {
        titleField.text = "";
        contentArea.text = "";
        sourceComboBox.currentIndex = 0;
        localRadio.checked = true;
        cloudRadio.checked = false;
        errorText.visible = false;
        errorText.text = "";
    }

    StackView.onActivating: {
        reloadSourceList();
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 16

        Text {
            typography: Typography.Title
            text: qsTr("上传文本")
        }

        Text {
            typography: Typography.Body
            color: Theme.currentTheme.colors.textSecondaryColor
            text: qsTr("填写以下信息以上传新的练习文本")
        }

        // 标题
        Text {
            typography: Typography.BodyStrong
            text: qsTr("标题")
        }

        TextField {
            id: titleField
            Layout.fillWidth: true
            placeholderText: qsTr("请输入文本标题")
        }

        // 来源
        Text {
            typography: Typography.BodyStrong
            text: qsTr("来源")
        }

        ComboBox {
            id: sourceComboBox
            Layout.fillWidth: true
            model: sourceListModel
            textRole: "label"
            valueRole: "key"
        }

        // 内容
        Text {
            typography: Typography.BodyStrong
            text: qsTr("内容")
        }

        TextArea {
            id: contentArea
            Layout.fillWidth: true
            Layout.minimumHeight: 200
            placeholderText: qsTr("请输入文本内容")
            wrapMode: TextArea.Wrap
        }

        // 上传目标
        Text {
            typography: Typography.BodyStrong
            text: qsTr("上传目标")
        }

        ColumnLayout {
            spacing: 4

            RadioButton {
                id: localRadio
                text: qsTr("本地文本库")
                checked: true
                onClicked: {
                    uploadPage.isCloud = false;
                    cloudRadio.checked = false;
                }
            }

            RadioButton {
                id: cloudRadio
                text: qsTr("云端（仅管理员）")
                enabled: appBridge ? appBridge.loggedin : false
                onClicked: {
                    uploadPage.isCloud = true;
                    localRadio.checked = false;
                }
            }
        }

        // 错误提示
        Text {
            id: errorText
            visible: false
            color: Theme.currentTheme.colors.systemCriticalColor
            typography: Typography.Caption
            Layout.fillWidth: true
            horizontalAlignment: Qt.AlignCenter
        }

        // 按钮区
        Item {
            Layout.fillHeight: true
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            Item {
                Layout.fillWidth: true
            }

            Button {
                text: qsTr("取消")
                onClicked: {
                    clearForm();
                }
            }

            Button {
                id: uploadBtn
                text: qsTr("上传")
                highlighted: true
                onClicked: {
                    var title = titleField.text.trim();
                    var content = contentArea.text.trim();
                    if (!title) {
                        errorText.text = qsTr("请输入标题");
                        errorText.visible = true;
                        return;
                    }
                    if (!content) {
                        errorText.text = qsTr("请输入内容");
                        errorText.visible = true;
                        return;
                    }
                    errorText.visible = false;
                    uploadBtn.enabled = false;
                    var sourceKey = sourceComboBox.currentValue;
                    if (appBridge)
                        appBridge.uploadText(title, content, sourceKey, uploadPage.isCloud);
                }
            }
        }
    }

    Connections {
        target: appBridge
        enabled: appBridge !== null
        function onUploadResult(success, message) {
            uploadBtn.enabled = true;
            if (success) {
                clearForm();
                // 成功提示
                errorText.text = qsTr("上传成功");
                errorText.color = Theme.currentTheme.colors.systemSuccessColor;
                errorText.visible = true;
            } else {
                errorText.text = message;
                errorText.color = Theme.currentTheme.colors.systemCriticalColor;
                errorText.visible = true;
            }
        }
        function onLoggedinChanged() {
            if (appBridge && !appBridge.loggedin) {
                uploadPage.isCloud = false;
                cloudRadio.checked = false;
                localRadio.checked = true;
            }
        }
    }
}
