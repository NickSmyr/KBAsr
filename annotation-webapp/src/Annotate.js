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
class Block extends React.Component {
  constructor(props) {
      super(props);
      this.transcr1 = props.transcr1
      this.transcr2 = props.transcr2
      this.state = {kbSelected : true}
      this.handleSwapClick.bind(this)
  }
  handleSwapClick(e){
      this.setState({kbSelected : ! this.state.kbSelected})
  }

  render() {
    let blocks;
    var swapButtonHidden = true
    // TODO refactor this
    var userPrompt
    if (this.state.kbSelected){
        if (this.transcr1 === this.transcr2){
            blocks = <BlockTranscription selected txt={this.transcr1}/>
        }
        else{
            swapButtonHidden = false
            blocks = <><BlockTranscription txt={this.transcr1}/><BlockTranscription selected txt={this.transcr2}/></>
        }
        userPrompt = this.transcr2
    }
    else {
        if (this.transcr1 === this.transcr2){
            blocks = <BlockTranscription selected txt={this.transcr1}/>
        }
        else{
            swapButtonHidden = false
            blocks = <><BlockTranscription selected txt={this.transcr1}/><BlockTranscription txt={this.transcr2}/></>
        }
        userPrompt = this.transcr1
    }

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
              <SwapButton hidden={swapButtonHidden} onclick={this.handleSwapClick.bind(this)}></SwapButton>
          </div>
          <div style={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center"
          }}>
                  <p contentEditable={"true"} onKeyDown={handleKeyDownOnInput.bind(this)} style={{
                      gridRow: 3,
                      border: "2px solid",
                      padding: "8px"
              }}>{userPrompt}</p>
          </div>

    </div>
  }
}
function SubmitButton(){
    return (
        <button style={{
            backgroundColor: "lightgreen",
            margin: "5px",
            borderRadius: "5px",
            width: "100px",
            height: "50px",
        }}>Submit</button>
    );
}

function Annotate() {
  return (<>
          <ReactAudioPlayer
  src="https://www2.cs.uic.edu/~i101/SoundFiles/BabyElephantWalk60.wav"
  controls
/>
    <div style={{
        display:"flex",
        flexDirection:"row"
    }}
         onKeyDown={handleKeyDownOnInput}
    >
        <div style={{
            padding: "5px",
            margin: "5px",
            textAlign: "center"
        }}>
            <p>Google ASR</p>
            <p>KB ASR</p>
        </div>
        <Block transcr1={"nya stället"} transcr2={"vi gör så rätt"}/>
        <Block transcr1={"mats"} transcr2={"mats"}/>
        <Block transcr1={"eller"} transcr2={"håller"}/>
        <Block transcr1={"ordning"} transcr2={"ordning"}/>
    </div>
      <SubmitButton></SubmitButton>
      </>


  );
}

export default Annotate;