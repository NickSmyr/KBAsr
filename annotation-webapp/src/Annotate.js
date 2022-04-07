import * as React from 'react';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';

import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography'
import Button from '@mui/material/Button';
import {Divider, Grid, Paper, Stack} from "@mui/material";
import "./Annotate.css"
import SwapVertIcon from '@mui/icons-material/SwapVert';
import {grey} from "@mui/material/colors";
import ReactAudioPlayer from 'react-audio-player';
import PlayCircleIcon from '@mui/icons-material/PlayCircle';
import PauseCircleIcon from '@mui/icons-material/PauseCircle';
import ReplayCircleFilledIcon from '@mui/icons-material/ReplayCircleFilled';


// A block that hold the transcription from a model
// TODO refactor common css
function BlockTranscription(props){
    let borderColor = "grey"
    if (props.selected){
        borderColor = "blue"
    }
    return <p style={{
        borderRadius: "20px",
        padding: "5px",
        margin: "5px",
        textAlign: "center",
        borderColor: borderColor,
        borderWidth: "3px",
        borderStyle: "solid",
        width: "auto",
        whiteSpace: "nowrap"
    }}>{props.txt}</p>
}

function SwapButton(props){
    var divStyle = {
        backgroundColor: "#b5b1a7",
        border: "2px solid",
        borderRadius: "150px",
        padding: "2px",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        maxWidth: "100px"
    }
    if (props.hidden){
        divStyle = {...divStyle, visibility: "hidden"}
    }

    return <div style={divStyle} onClick={props.onclick}>
        <SwapVertIcon></SwapVertIcon>
    </div>
}
function UserPromptBlock(props){
    var progress = props.progress
    var progressPercentStr = Math.round(progress * 100).toString()
    var repeatStyle = {}
    if (props.blockRepeated){
        repeatStyle={
            border: "2px solid",
            borderColor: "blue"
        }
    }
    return (
        <div style={{
            backgroundColor: "lightgrey",
            margin: "5px",
            borderRadius: "10px",
            display: "grid",
            gridRow: 3,
            width: "auto",
            gridTemplateColumns: "max-content",
            position: "relative",
            zIndex: -1,
        }}
        >
            <div style={{
                backgroundColor: "lightgreen",
                position: "absolute",
                height: "100%",
                width: progressPercentStr + "%",
                zIndex: 0,
                borderRadius: "10px",
            }}
            >

            </div>
            <div style={{
                display: "flex",
                zIndex: "99"
            }}>
                <button tabIndex={-1} onClick={(e) => props.onPlay()}>
                    <PlayCircleIcon sx={{
                        zIndex: 1
                        }}
                    />
                </button>

                <button tabIndex={-1} onClick={(e) => props.onPause()}>
                    <PauseCircleIcon sx={{
                        zIndex: 1
                        }}
                    />
                </button>

                <button style={repeatStyle} tabIndex={-1} onClick={(e) => props.onRepeat()}>
                    <ReplayCircleFilledIcon sx={{
                        zIndex: 1
                        }}
                    />
                </button>

            </div>
            <p contentEditable={"true"} style={{
                      gridRow: 2,
                      padding: "8px",
                      margin: "5px",
                      textAlign: "center",
                      overflow: "hidden",
                      MozAppearance: "none",
                      width: "auto",
                      whiteSpace: "nowrap",
                      zIndex: "1"
                  }}
                    onClick={(e) => console.log("paragraph clicked")}
                    onKeyDown={(e) => {
                      if (e.code === "Enter"){
                          e.preventDefault()
                          props.onSubmit()
                      }
                  }} onInput={props.onChange}
                     suppressContentEditableWarning={true}
                     ref={props.userPromptRef}
                  >{props.userPrompt}
            </p>
        </div>
    )
}
// A Pair of blocks that contain the transcriptions from both models, the swap button and the final text input
// Props transcr1, transcr2, kbSelected, onclick, selectedTranscription
function Block(props){
    let blocks;
    var swapButtonHidden = false

    if (props.transcr1 === props.transcr2){
        swapButtonHidden = true
        blocks = <>
            <BlockTranscription selected={true} txt={props.transcr1}/>
        </>
    }
    else{
        blocks = <>
            <BlockTranscription selected={!props.kbSelected} txt={props.transcr1}/>
            <BlockTranscription selected={props.kbSelected} txt={props.transcr2}/>
        </>
    }
    // Row grid contains transcription blocks, swap buttin and text input
      return <div style={{
          display: "grid"
      }}>

          <div style={{
              display : "flex",
              flexDirection: "column",
              maxWidth: "100%",
              minHeight : "200px",
              justifyContent: "center",
              alignItems: "center",
              gridRow: 1
            }
          }>
              {blocks}
          </div>
          <div style={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center"
          }}>
              <SwapButton hidden={swapButtonHidden} onclick={props.onclick}/>
          </div>
          <div style={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              zIndex: 0
          }}>
              <UserPromptBlock onChange={props.onChange} userPromptRef={props.userPromptRef}
                onSubmit={props.onSubmit} progress={props.progress} onPlay={props.onPlay}
                               onPause={props.onPause} onRepeat={props.onRepeat} blockRepeated={props.blockRepeated}
              />
          </div>

    </div>
  }
function SubmitButton(props){
    return (
        <button style={{
            backgroundColor: "lightgreen",
            margin: "5px",
            borderRadius: "5px",
            width: "100px",
            height: "50px",
        }}
                onClick={props.onSubmit}
        >Submit</button>
    );
}

// Annotation screen component. Data arguments are blocks (transcription blocks)
// And when submitting it should make a post request to the backend with the result
// Props:
//          blocks: A list of blocks (tuples) containing transcriptions. Each tuple is
//                  (googleTranscription, kbTranscription)
//          onSubmit: A callback that is called when the user has finished annotating the utterance. The parameters
//                  passed to the callback is the final concatenated transcription string
//          blockEndTimes: A list containing the end times in seconds for each of the blocks
class Annotate extends React.Component {
    constructor(props) {
        super(props);
        this.userPromptRefs= props.blocks.map((x) => React.createRef())
        this.state = {
            googleBlocks : props.blocks.map((x) => x[0]),
            kbBlocks : props.blocks.map((x) => x[1]),
            selectedTranscriptions : props.blocks.map((x) => x[1]),
            kbSelected : props.blocks.map((x) => true),
            // We have to disconnect the user prompts from reacts rendering logic
            userEdited: props.blocks.map((x) => false),
            blockProgresses: props.blocks.map((x) => 0),
            blockRepeated: props.blocks.map((x) => false)
        }
        this.getSelectedTranscriptions = this.getSelectedTranscriptions.bind(this)
        this.handleChange = this.handleChange.bind(this)
        this.componentDidMount = this.componentDidMount.bind(this)
        this.onSubmit = this.onSubmit.bind(this)
        this.blockEndTimes = props.blockEndTimes
        this.listenCallback = this.listenCallback.bind(this)
        this.rap = undefined
    }
    // On submit used in the components children
    onSubmit(){
        this.props.onSubmit(this.getSelectedTranscriptions())
    }
    getSelectedTranscriptions(){
        // ContentEditable in userInput makes user input add a newline at the end (somtimes)
        var selectedTranscriptions = this.state.selectedTranscriptions.map((x) => {
            if (x[x.length -1] === "\n"){
                return x.substring(0, x.length -1)
            }
            else{
                return x
            }
        })
        return selectedTranscriptions.join(" ")
    }
    // We have to use the initial values
    componentDidMount() {
        this.props.blocks.forEach((e,i) => {
            this.userPromptRefs[i].current.innerHTML = this.state.selectedTranscriptions[i]
        })
        this.userPromptRefs[0].current.focus()
        // document.addEventListener("click", (e) =>{
        //     console.log("Got click event ", e)
        // })
    }
    // Handles the change of event e at block index i
    handleChange(e, i){
        this.setState(prevState => {

            var newTr = [...prevState.selectedTranscriptions]
            var newUserEdited = [...prevState.userEdited]
            if (! newUserEdited[i]){
                e.preventDefault()
            }

            newTr[i] = e.target.innerText
            newUserEdited[i] = true
            return {selectedTranscriptions: newTr,
                userEdited: newUserEdited
            }
        })
    }

    // Called when a user presseses the play button on one of the UserPrompts
    // i is the position of the user prompt
    userPromptPlay(i){
        // Play should override any results
        this.setState({blockRepeated: this.state.blockRepeated.map((x) => false)})

        if (i === 0){
            this.rap.audioEl.current.currentTime = 0
        }
        else {
            this.rap.audioEl.current.currentTime = this.blockEndTimes[i-1]
        }
        this.rap.audioEl.current.play()
    }

    // Called when a user presseses the pause button on one of the UserPrompts
    // i is the position of the user prompt
    userPromptPause(i){
        this.rap.audioEl.current.pause()
    }
    // Called when a user presseses the pause button on one of the UserPrompts
    // i is the position of the user prompt
    userPromptRepeat(i){
        this.setState(prevState => {
            var newBlockRepeated = prevState.blockRepeated.map((x)=> false)
            // Only repeat the block clicked if it was not already repeated
            // Otherwise it will be toggled
            if (! prevState.blockRepeated[i]){
                newBlockRepeated[i] = true
            }
            return {blockRepeated : newBlockRepeated}
        })
    }

    // Updates the progresses shown in user prompts whenever a listen event is emitted from the Audio player
    listenCallback(currTime){
        // Index of the repeat block
        var repeatBlockIdx = this.state.blockRepeated.indexOf(true)
        // set audio players time to block start time if there is at least one repeated block
        //  and the current time is past the blocks end time
        if (repeatBlockIdx !== -1 && this.rap.audioEl.current.currentTime >  this.blockEndTimes[repeatBlockIdx] ){
           if (repeatBlockIdx === 0){
               this.rap.audioEl.current.currentTime = 0
           }
           else{
               console.log("Setting audio player time to ", this.blockEndTimes[repeatBlockIdx-1])
               this.rap.audioEl.current.currentTime = this.blockEndTimes[repeatBlockIdx-1]
           }
        }
        // Update progress in react state
        this.setState(prevState => {
            var newBlockProgresses = this.props.blockEndTimes.map((e,i,a) =>{
                if (currTime > e){
                    return 1
                }
                else{
                    if (i===0){
                        return currTime / e
                    }
                    else{
                        // If the block has not started yet
                        if (currTime < a[i-1]){
                            return 0
                        }
                        else{
                            return (currTime - a[i-1]) / (e - a[i-1])
                        }
                    }
                }
            })
            return {blockProgresses : newBlockProgresses}
        })
    }
    render(){
      return (<>
          <ReactAudioPlayer
              src="/file_7.wav"
              controls
              onListen={this.listenCallback}
              listenInterval={0.001}
              ref={(element) => { this.rap = element; }}
          />
          <div style={{
            display:"flex",
            flexDirection:"row",
            flexWrap: "nowrap",
            overflowX: "auto"
            }}
            >
              <div style={{
                    padding: "5px",
                    margin: "5px",
                    maxHeight: "190px",
                    minWidth: "100px",
                    textAlign: "center",
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "center"
                }}>
                    <p>Google ASR</p>
                    <p>KB ASR</p>
                </div>
            <div style={{
                display:"flex",
                flexDirection:"row",
                flexWrap: "nowrap",
                overflowX: "auto"
            }}
            >
                {
                    this.state.googleBlocks.map((e,i)=>{
                        var blockOnClick = this.blockOnClick(i);

                        return <Block transcr1={this.state.googleBlocks[i]} transcr2={this.state.kbBlocks[i]}
                                      kbSelected={this.state.kbSelected[i]} onclick={blockOnClick.bind(this)}
                                      onSubmit={this.onSubmit} onChange={(e)=>{
                                          return this.handleChange(e,i)
                                      }}
                                      userPromptRef={this.userPromptRefs[i]}
                                      progress={this.state.blockProgresses[i]}
                                      onPlay={() => this.userPromptPlay(i)}
                                      onPause={() => this.userPromptPause(i)}
                                      onRepeat={() => this.userPromptRepeat(i)}
                                      blockRepeated={this.state.blockRepeated[i]}
                        />
                    })
                }
            </div>
          </div>
              <SubmitButton onSubmit={this.onSubmit}/>
              </>
    );
    }

    blockOnClick(i) {
        var blockOnClick = (e) => {
            this.setState(prevState => {
                var newKbselected = [...prevState.kbSelected]
                newKbselected[i] = !newKbselected[i]
                var newSelectedTranscriptions = [...prevState.selectedTranscriptions];
                if (newKbselected[i]) {
                    newSelectedTranscriptions[i] = this.state.kbBlocks[i]
                    this.userPromptRefs[i].current.innerHTML = this.state.kbBlocks[i]
                } else {
                    newSelectedTranscriptions[i] = this.state.googleBlocks[i]
                    this.userPromptRefs[i].current.innerHTML = this.state.googleBlocks[i]
                }
                return {
                    kbSelected: newKbselected,
                    selectedTranscriptions: newSelectedTranscriptions
                }
            })
        }
        return blockOnClick;
    }
}
export default Annotate;