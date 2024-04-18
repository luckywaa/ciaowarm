1. 小沃目前支持接入Home Assistant的产品有：

    - 小沃精灵
    - 小沃精灵S1
    - 星联网关
    - 小融网关
    - 小沃壁挂炉
    - 小沃房间温控器
    - 星联网关已完成适配的第三方壁挂炉


2. 接入步骤：

    - 通过应用市场下载并安装小沃云家App（Android和iOS都可以），通过手机号完成登录与绑定设备操作。
    - 点击此链接 ([获取授权码](https://cloud.ciaowarm.com/halogin.html))，通过手机号（注：输入的手机号需与步骤1的登录手机号一致）获取授权码，保存获取到的授权码。
    - 将ciaowarm文件夹复制到Home Assistant的custom_components文件夹下，并重启Home Assistant。
    - 点击Home Assistant左侧导航栏“配置”，点击"设备与服务"，点击右下角的“添加集成”，选择“Ciaowarm”品牌，在上面的输入框内输入步骤1和2所用的手机号，在下面的输入框内输入步骤2获取到的授权码，点击“提交”，即可完成接入。

   
3. 支持的参数：

    温控器：

   |      参数名      | 操作权限 |
   | :--------------: | :------: |
   |      网关ID      |   只读   |
   |     温控器ID     |   只读   |
   |  温控器在线状态  |   只读   |
   |    温控器名称    |   只读   |
   |     室内温度     |   只读   |
   | 离家模式目标温度 |  可读写  |
   | 居家模式目标温度 |  可读写  |
   | 睡眠模式目标温度 |  可读写  |
   |       模式       |  可读写  |

   

    小沃壁挂炉：

   |         参数名         |                      操作权限                      |
   | :--------------------: | :------------------------------------------------: |
   |         网关ID         |                        只读                        |
   |        壁挂炉ID        |                        只读                        |
   |     壁挂炉在线状态     |                        只读                        |
   |         开关机         |                       可读写                       |
   |        冬夏模式        |                       可读写                       |
   | 自动控制采暖水目标温度 |                       可读写                       |
   |   卫浴水短时预热开关   |    可读写（仅在壁挂炉支持卫浴水预热功能时开放）    |
   |     采暖水目标温度     | 自动控制采暖水目标温度功能禁止时可读写；允许时只读 |
   |     卫浴水目标温度     |                       可读写                       |
   |     采暖水出水温度     |                        只读                        |
   |     卫浴水出水温度     |                        只读                        |
   |         故障码         |                        只读                        |
   |        火焰状态        |                        只读                        |
   |         水压值         |                        只读                        |

   

    第三方壁挂炉：

   |     参数名     |               读写               |
   | :------------: | :------------------------------: |
   |     网关ID     |               只读               |
   |  网关在线状态  |               只读               |
   |    自动控制    |              可读写              |
   |    采暖允许    |              可读写              |
   |    卫浴允许    |              可读写              |
   | 采暖水目标温度 | 自动控制禁止时可读写；允许时只读 |
   | 卫浴水目标温度 |              可读写              |
   | 采暖水实际温度 |               只读               |
   | 卫浴水实际温度 |               只读               |
   |     故障码     |               只读               |

---
### English instruction

1. Ciaowarm currently supports the following products for integration with Home Assistant:

   - Ciaowarm Smart
   - Ciaowarm Smart S1
   - Starlink Gateway
   - Halowarm Gateway
   - Ciaowarm Wall-mounted Boiler
   - Ciaowarm room thermostat
   - Third-party Wall-mounted Boilers compatible with Starlink Gateway

2. Integration Steps:

   - Download and install the Ciaowarm App from the App store (available for both Android and iOS). Log in and bind devices using your phone number.
   - Click on this link ([Get Authorization Code](https://cloud.ciaowarm.com/halogin.html) and obtain the authorization code by entering your phone number (Note: The phone number entered must match the one used for login in step 1). Save the obtained authorization code.
   - Copy the "ciaowarm" folder to the "custom_components" folder in Home Assistant, and restart Home Assistant.
   - Click on the "Configuration" tab on the left sidebar of Home Assistant, then click on "Devices & Services", and finally click on "Add Integration" in the bottom right corner. Select the "Ciaowarm" brand, enter the phone number used in steps 1 and 2 in the input box above, enter the authorization code obtained in step 2 in the input box below, click "Submit", and you will have completed the integration.

3. Supported Parameters:

   Thermostat:

   | Parameter Name                | Operation Permission |
   | ----------------------------- | -------------------- |
   | Gateway ID                    | Read-only            |
   | Thermostat ID                 | Read-only            |
   | Thermostat Online State       | Read-only            |
   | Thermostat Name               | Read-only            |
   | Indoor Temperature            | Read-only            |
   | Away Mode Target Temperature  | Read-write           |
   | Home Mode Target Temperature  | Read-write           |
   | Sleep Mode Target Temperature | Read-write           |
   | Mode                          | Read-write           |

   Ciaowarm Wall-mounted Boiler:

   | Parameter Name                                        | Operation Permission                                         |
   | ----------------------------------------------------- | ------------------------------------------------------------ |
   | Gateway ID                                            | Read-only                                                    |
   | Boiler ID                                             | Read-only                                                    |
   | Boiler Online State                                   | Read-only                                                    |
   | Power On/Off                                          | Read-write                                                   |
   | Winter/Summer Mode                                    | Read-write                                                   |
   | Automatic Control of Heating Water Target Temperature | Read-write                                                   |
   | Bathroom Water Short-term Preheating Switch           | Read-write (Only available when the boiler supports bathroom water preheating) |
   | Heating Water Target Temperature                      | Read-write when Automatic Control of Heating Water Target Temperature is disabled; Read-only when enabled |
   | Bathroom Water Target Temperature                     | Read-write                                                   |
   | Heating Water Outlet Temperature                      | Read-only                                                    |
   | Bathroom Water Outlet Temperature                     | Read-only                                                    |
   | Fault Code                                            | Read-only                                                    |
   | Flame Status                                          | Read-only                                                    |
   | Water Pressure Value                                  | Read-only                                                    |

   Third-party Wall-mounted Boiler:

   | Parameter Name                    | Operation Permission                                         |
   | --------------------------------- | ------------------------------------------------------------ |
   | Gateway ID                        | Read-only                                                    |
   | Gateway Online State              | Read-only                                                    |
   | Automatic Control                 | Read-write                                                   |
   | Heating Allowance                 | Read-write                                                   |
   | Bathroom Allowance                | Read-write                                                   |
   | Heating Water Target Temperature  | Read-write when Automatic Control is disabled; Read-only when enabled |
   | Bathroom Water Target Temperature | Read-write                                                   |
   | Heating Water Actual Temperature  | Read-only                                                    |
   | Bathroom Water Actual Temperature | Read-only                                                    |
   | Fault Code                        | Read-only                                                    |
   