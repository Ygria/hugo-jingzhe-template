---
title: Vue + WebSocket + WaveSurferJS 实现H5聊天对话交互
date:  2020-10-22
tags:
- 编程
- 前端
---

# 引言
在与实现了语音合成、语义分析、机器翻译等算法的后端交互时，页面可以设计成更为人性化、亲切的方式。我们采用类似于聊天对话的实现，效果如下：
- **智能客服**（输入文本，返回引擎处理后的文本结果）
![85b8e7f52c9b329bfe65fc810f133a31.gif](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/85b8e7f52c9b329bfe65fc810f133a31.gif)



- **语音合成**（输入文本，返回文本以及合成的音频）
![语音合成.gif](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/%E8%AF%AD%E9%9F%B3%E5%90%88%E6%88%90.gif)


如上图所示，返回文本后，再返回合成出的音频。
音频按钮嵌在对话气泡中，可以点击播放。

- **语音识别**（在页面录制语音发送，页面实时展示识别出的文本结果）
![语音识别.gif](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/%E8%AF%AD%E9%9F%B3%E8%AF%86%E5%88%AB.gif)

# 实现功能及技术要点
**1、基于WebSocket实现对话流** 
页面与后端的交互是实时互动的，所以采用WebSocket协议，而不是HTTP请求，这样后端推送回的消息可以实时显示在页面上。
WebSocket的返回是队列的、无序的，在后续处理中我们也需要注意这一点，在后文中会说到。
**2、调用设备麦克风进行音频录制和转码加头，基于WebAudio、WaveSurferJS等实现音频处理和绘制**
**3、基于Vue的响应式页面实现**
**4、CSS3 + Canvas + JS 交互效果优化**
- 录制音频CSS动画效果
- 聊天记录自动滚动
下面给出部分实现代码。

# 集成WebSocket
我们的聊天组件是页面侧边打开的抽屉（`el-drawer`），Vue组件会在打开时创建，关闭时销毁。在组件中引入WebSocket，并管理它的开、关、消息接收和发送，使它的生命周期与组件一致（打开窗口时创建ws连接，关闭窗口时关闭连接，避免与后台连接过多。）
  ```javascript
created(){
     if (typeof WebSocket === 'undefined') {
        alert('您的浏览器不支持socket')
      } else {
        // 实例化socket
        this.socket = new WebSocket(this.socketServerPath)
        // 监听socket连接
        this.socket.onopen = this.open
        // 监听socket错误信息
        this.socket.onerror = this.error
        // 监听socket消息
        this.socket.onmessage = this.onMessage
        this.socket.onclose = this.close
      }
}
destroyed(){
    this.socket.close()
}
```
如上，将WebSocket的事件绑定到JS方法中，可以在对应方法中实现对数据的接收和发送。
打开浏览器控制台，选中指定的标签，便于对`WebSocket`连接进行监控和查看。
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417141841.png)



# 音频录制采集
从浏览器端音频和视频采集基于网页即时通信（Web Real-Time
 Communication，简称`WebRTC`） 的API。通过`WebRTC`的`getUserMedia`实现，获取一个`MediaStream`对象，将该对象关联到AudioContext即可获得音频。 
> 可参考RecorderJS的实现： https://github.com/mattdiamond/Recorderjs/blob/master/examples/example_simple_exportwav.html

```javascript
if (navigator.getUserMedia) {
      navigator.getUserMedia(
        { audio: true }, // 只启用音频
        function(stream) {
          var context = new(window.webkitAudioContext || window.AudioContext)()
          var audioInput = context.createMediaStreamSource(stream)
          var recorder = new Recorder(audioInput)

        },
        function(error) {
          switch (error.code || error.name) {
            case 'PERMISSION_DENIED':
            case 'PermissionDeniedError':
              throwError('用户拒绝提供信息。')
              break
            case 'NOT_SUPPORTED_ERROR':
            case 'NotSupportedError':
              throwError('浏览器不支持硬件设备。')
              break
            case 'MANDATORY_UNSATISFIED_ERROR':
            case 'MandatoryUnsatisfiedError':
              throwError('无法发现指定的硬件设备。')
              break
            default:
              throwError('无法打开麦克风。异常信息:' + (error.code || error.name))
              break
          }
        }
      )
    } else {
      throwError('当前浏览器不支持录音功能。')
    }
```
>注意： 若navigator.getUserMedia获取到的是`undefined`，是Chrome浏览器的安全策略导致的，需要通过https请求或配置浏览器，配置地址： chrome://flags/#unsafely-treat-insecure-origin-as-secure

> 浏览器采集到的音频为PCM格式(`PCM` （脉冲编码调制  `Pulse Code Modulation`）)，需要对音频加头才能在页面上进行播放。注意加头时采样率、采样频率、声道数量等必须与采样时相同，不然加完头后的音频无法解码。参考查看https://github.com/mattdiamond/Recorderjs/blob/master/src/recorder.js中`exportWav`方法。

业务中对接的语音识别引擎为实时转写引擎，即：不是录制完成后再发送，而是一边录制一边进行编码并发送。
使用`onaudioprocess`方法监听语音的输入：
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417142734.png)

参考这个实现，我们可以在每次监听到有数据写入时，从buffer中获取到录制到的数据，并进行编码、压缩，再通过WebSocket发送。

#  Vue组件设计和业务实现
分析页面业务逻辑，将代码拆分成两个组件：
`ChatDialog.vue` 聊天对话框页面，根据输入类型，分为文本输入、语音输入。
`ChatRecord.vue`聊天记录组件，根据发送方（自己或者系统）展示向左/向右的气泡，根据内容显示文本、音频等。`ChatDialog`是`ChatRecord`的父组件，遍历`ChatDialog`中的`chatList`对象（`Array`），将`chatList`中的项注入到`ChatRecord`中。
```html
<div class="chat-list">
            <div v-for="(item,index) in chatList" :key="index" class="msg-wrapper">
                <chat-record ref="chatRecord" :data="item" @showJson="showJsonDialog"></chat-record>
            </div>
            <div id="msg_end" style="height:0px; overflow:hidden"></div>
        </div>
</div>
```
对于聊天记录的气泡展示，与数据类型相关性很强，`ChatRecord`组件只关心对数据的处理和展示，我们可以完全不用关心消息的发送、接收、音频的录制、停止录制、接受音频等逻辑，只需要根据数据来展示不同的样式即可。
**这样Vue的响应式就充分获得了用武之地**：无需用代码对样式展示进行控制，只需要设计合理的数据格式和样式模板，然后注入不同的数据即可。
模板页面： 使用`v-if`控制，修改`chatList`里的对象内容即可改变页面展示。

根据业务需求，将`ChatRecord`可能接收到的数据分为以下几类：

发送方为自己：
- 文本输入，显示文本
实现简单，不做赘述。
- 语音输入 Loading状态，显示波纹动画和计时
![wave.gif](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/wave.gif)

计时器使用JS的`setInterval`方法，每100ms更新一次录制时长
```javascript
 this.recordTimer = setInterval(() => {
        this.audioDuration = this.audioDuration + 0.1
      }, 100)
```
停止后清空计时器：
```javascript
 clearInterval(this.recordTimer)
```


- 语音输入完毕，根据录制的语音，绘制波纹
效果：
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417142409.png)


使用`wavesurfer`插件:
```javascript
 initWaveSurfer() {
      this.$nextTick(() => {
        this.wavesurfer = WaveSurfer.create({
          container: this.$refs.waveform,
          height: 20,
          waveColor: '#3d6fff',
          progressColor: 'blue',
          backend: 'MediaElement',
          mediaControls: false,
          audioRate: '1',
          fillParent: false,
          maxCanvasWidth: 500,
          barWidth: 1,
          barGap: 2,
          barHeight: 5,
          barMinHeight: 3,
          normalize: true,
          cursorColor: '#409EFF'
        })
        this.convertAudioToUrl(this.waveAudio).then((res) => {
          this.wavesurfer.load(res)

          setTimeout(() => {
            this.audioDuration = this.getAudioDuration()
          }, 100)
        })
      })
    },

   // 将音频转化成url地址
    convertAudioToUrl(audio) {
      let blobUrl = ''
      if (this.data.sendBy === 'self') {
        blobUrl = window.URL.createObjectURL(audio)
        return new Promise((resolve) => {
          resolve(blobUrl)
        })
      } else {
        return this.base64ToBlob({
          b64data: audio,
          contentType: 'audio/wav'
        })
      }
    },

    base64ToBlob({ b64data = '', contentType = '', sliceSize = 512 } = {}) {
      return new Promise((resolve, reject) => {
        // 使用 atob() 方法将数据解码
        let byteCharacters = atob(b64data)
        let byteArrays = []
        for (
          let offset = 0;
          offset < byteCharacters.length;
          offset += sliceSize
        ) {
          let slice = byteCharacters.slice(offset, offset + sliceSize)
          let byteNumbers = []
          for (let i = 0; i < slice.length; i++) {
            byteNumbers.push(slice.charCodeAt(i))
          }
          // 8 位无符号整数值的类型化数组。内容将初始化为 0。
          // 如果无法分配请求数目的字节，则将引发异常。
          byteArrays.push(new Uint8Array(byteNumbers))
        }
        let result = new Blob(byteArrays, {
          type: contentType
        })
        result = Object.assign(result, {
          // 这里一定要处理一下 URL.createObjectURL
          preview: URL.createObjectURL(result),
          name: `XXX.wav`
        })
        resolve(window.URL.createObjectURL(result))
      })
    },
```

--- 
发送方为系统：
- 仅返回文本：显示文本
- 仅返回音频（参考发送方为自己的实现）
 ![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417142600.png)


- 返回文本，随即返回文本对应的合成音频，显示文本和播放按钮
![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417142626.png)

![image.png](https://cdn.jsdelivr.net/gh/Ygria/Pictures@main/20240417142644.png)


 

页面嵌入audio标签，将hidden设置为true使其不显示：
```html
<div class="audio-player">
          <svg-icon v-if="!isPlaying" icon-class='play' @click="onClickAudioPlayer" />
          <svg-icon v-else icon-class='pause' @click="onClickAudioPlayer" />
          <audio :src="playAudioUrl" autostart="true" hidden="true" ref="audioPlayer" />
        </div>
```
`playAudioUrl`的生成参考上面生成的`wavesurfer`的url。
使用`isPlaying`参数记录当前音频的播放状态，并使用`setTimeout`方法，当播放了音频时长后，将播放按钮自动置为`play`。
```javascript
  onClickAudioPlayer() {
      if (this.isPlaying) {
        this.$refs.audioPlayer.pause()
        this.isPlaying = false
      } else {
        // 每次点击时，开始播放，并在播放完毕将isPlaying置为false
        this.$refs.audioPlayer.currentTime = 0
        this.$refs.audioPlayer.play()
        this.isPlaying = true

        setTimeout(() => {
          // 将正在播放重置为false
          this.isPlaying = false
        }, Math.ceil(this.$refs.audioPlayer.duration) * 1000)
      }
    },
```


- 聊天记录自动定位到最后一条：
使用`scrollIntoView()`方法
- 记录每次会话对应的记录ID（`recordId`）：
定义单次会话的id，并在返回的消息中回传，从而建立多条`websocket`返回的关联关系。
--- 
以上就是全部实现。难点主要是请求麦克风权限和对音频进行编码，**在加wav头时必须保证和采样时的采样率、频率一致** 。