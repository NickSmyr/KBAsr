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
        borderStyle: "solid"
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

function handleKeyDownOnInput(e){
      if (e.key === 'Enter') {
        alert('Enter pressed, submitted');
        e.preventDefault()
      }
  }
// A Pair of blocks that contain the transcriptions from both models, the swap button and the final text input
// Props transcr1, transcr2, kbSelected, onclick, selectedTranscription
function Block(props){
    let blocks;
    var swapButtonHidden = true
    // TODO refactor this
    var userPrompt = props.selectedTranscription
    if (props.kbSelected){
        if (props.transcr1 === props.transcr2){
            blocks = <BlockTranscription selected txt={props.transcr1}/>
        }
        else{
            swapButtonHidden = false
            blocks = <><BlockTranscription txt={props.transcr1}/><BlockTranscription selected txt={props.transcr2}/></>
        }
    }
    else {
        if (props.transcr1 === props.transcr2){
            blocks = <BlockTranscription selected txt={props.transcr1}/>
        }
        else{
            swapButtonHidden = false
            blocks = <><BlockTranscription selected txt={props.transcr1}/><BlockTranscription txt={props.transcr2}/></>
        }
    }
        //console.log("Props on change ", props.onChange)
    // Row grid contains transcription blocks, swap buttin and text input
      return <div style={{
          display: "grid"
      }}>

          <div style={{
              display : "flex",
              flexDirection: "column",
              maxWidth: "100%",
              height : "100px",
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
              alignItems: "center"
          }}>
              <div style={{
                  overflow: "hidden",
                  float: "none",
                  width: "8em"
              }}>
                  <input contentEditable={"true"} style={{
                      gridRow: 3,
                      border: "2px solid",
                      padding: "8px",
                      margin: "5px",
                      textAlign: "center",
                      overflow: "hidden",
                  }} onKeyDown={(e) => {
                      if (e.code === "Enter"){
                          e.preventDefault()
                          props.onSubmit()
                      }
                  }} onInput={props.onChange}
                     suppressContentEditableWarning={true}
                     value={userPrompt}
                  />
              </div>
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
class Annotate extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            googleBlocks : props.blocks.map((x) => x[0]),
            kbBlocks : props.blocks.map((x) => x[1]),
            selectedTranscriptions : props.blocks.map((x) => x[1]),
            kbSelected : props.blocks.map((x) => true)
        }
        this.onSubmit = this.onSubmit.bind(this)
        this.handleChange = this.handleChange.bind(this)
    }

    onSubmit(){
        var selectedTranscription = this.state.selectedTranscriptions.join(" ")
        alert("Received response: " + selectedTranscription)
    }
    // Handles the change of event e at block index i
    handleChange(e, i){
        console.log("Inside handle Change with params ", e,i)
        this.setState(prevState => {
            var newTr = [...prevState.selectedTranscriptions]
            if (!e.target.value){
              newTr[i] = e.target.innerText
            }
            else {
              newTr[i] = e.target.value
            }
            console.log("Target innerText ", e.target.innerText)
            console.log("Target value ", e.target.value)
            console.log("Target innerHTML ", e.target.innerHTML)

            return {selectedTranscriptions: newTr}
        })
    }

    render(){
      return (<>
          <ReactAudioPlayer
              src="https://www2.cs.uic.edu/~i101/SoundFiles/BabyElephantWalk60.wav"
              controls
          />
            <div style={{
                display:"flex",
                flexDirection:"row"
            }}
            >
                <div style={{
                    padding: "5px",
                    margin: "5px",
                    textAlign: "center"
                }}>
                    <p>Google ASR</p>
                    <p>KB ASR</p>
                </div>
                {
                    this.state.googleBlocks.map((e,i)=>{
                        var blockOnClick = (e) => {
                            this.setState(prevState => {
                                var newKbselected = [...prevState.kbSelected]
                                newKbselected[i] = !newKbselected[i]
                                var newSelectedTranscriptions = [...prevState.selectedTranscriptions];
                                if (newKbselected[i]){
                                    newSelectedTranscriptions[i] = this.state.kbBlocks[i]
                                }
                                else{
                                    newSelectedTranscriptions[i] = this.state.googleBlocks[i]
                                }
                                return {kbSelected : newKbselected,
                                    selectedTranscriptions: newSelectedTranscriptions
                                }
                            })
                        }
                        return <Block transcr1={this.state.googleBlocks[i]} transcr2={this.state.kbBlocks[i]}
                                      kbSelected={this.state.kbSelected[i]} onclick={blockOnClick.bind(this)}
                                      selectedTranscription={this.state.selectedTranscriptions[i]}
                                      onSubmit={this.onSubmit} onChange={(e)=>{
                                          console.log("Handling change")
                                          return this.handleChange(e,i)
                        }}
                        />
                    })
                }
            </div>
              <SubmitButton onSubmit={this.onSubmit}/>
              </>
    );
    }

}
function submitResponse(txt){
    console.log("Submitting response ", txt)
}
export default Annotate;