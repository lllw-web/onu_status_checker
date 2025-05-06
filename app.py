import streamlit as st
import requests

# 状态码映射
STATUS_MAPPING = {
    "1": "在线",
    "2": "离线",
    "3": "掉电",
    "5": "掉电",
    "7": "离线"
}

# 获取 ONU 状态
def get_onu_status(device_ip):
    url = "https://cnioc.telecomjs.com:18080/serv/atom-center/atom/v1.0/atom_center/OLTAllONUState"
    headers = {
        "app-key": "739DF75555643C5EC85C9F6AEEA07D2D",
        "staffcode": "TZ64733"
    }
    data = {"DeviceIP": device_ip}
    try:
        response = requests.post(url, headers=headers, json=data)
        status = response.json()['data']['atom_data']['AllStatus']
        return status
    except Exception as e:
        st.error(f"获取ONU状态失败：{e}")
        return None

# 获取接入资源
def get_onu_res(acc_number):
    url = "https://cnioc.telecomjs.com:18080/serv/atom-center/atom/v1.0/atom_center/OSS_USER_RESOURCE"
    headers = {
        "app-key": "73DB4D73C2AD1F7CD4F5408A6D6C1541",
        "staffcode": "TZ64733"
    }
    data = {
        "accessNumber": acc_number,
        "areaCode": "tz.js.cn"
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()['data']['atom_data']['devInfo']
    except Exception as e:
        st.error(f"获取资源失败：{e}")
        return None

# 获取第二管理地址
def get_second_ip(ip):
    url = "https://cnioc.telecomjs.com:18080/serv/atom-center/atom/v1.0/atom_center/IPOSS_DEV_RESOURCE"
    headers = {
        "app-key": "CCE0EFE2A5E4C319A27399F5F0908F69",
        "staffcode": "TZ64733"
    }
    data = {"DeviceIP": ip}
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()['data']['atom_data']
    except Exception as e:
        st.error(f"获取第二管理IP失败：{e}")
        return None

# Streamlit 页面
st.title("ONU 状态查询工具")
acc_input = st.text_input("请输入接入号（多个用英文逗号分隔）:")

if st.button("开始查询") and acc_input:
    acc_list = [acc.strip() for acc in acc_input.split(",") if acc.strip()]
    for acc in acc_list:
        st.markdown(f"### 🔍 接入号：{acc}")
        res_info = get_onu_res(acc)
        if not res_info:
            st.error(f"❌ 获取资源失败：{acc}")
            continue

        device_ip = res_info.get("deviceIp", "")
        loid = res_info.get("loId", "")
        st.write("📋 资源信息：", res_info)

        second_ip = ""
        if device_ip:
            second_info = get_second_ip(device_ip)
            if second_info:
                second_ip = second_info.get("loopback_ip_2nd", "")
                st.write("🌐 第二管理IP：", second_ip)

        if second_ip and loid:
            status_info = get_onu_status(second_ip)
            status = status_info.get(loid, "") if status_info else ""
            mapped = STATUS_MAPPING.get(status, f"未知状态码：{status}")
            st.success(f"✅ ONU 状态（LOID={loid}）：{mapped}")
        else:
            st.warning("⚠️ 缺少第二管理IP或LOID，无法获取状态")
