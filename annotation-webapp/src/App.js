import * as React from 'react';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';

import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography'
import Button from '@mui/material/Button';
import {Grid} from "@mui/material";

function Item(){
    return  <Card sx={{ maxWidth: 345, backgroundColor: "#c5cff0" }}>
        <CardContent>
        <Typography gutterBottom variant="h5" component="div">
          Lizard
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Lizards are a widespread group of squamate reptiles, with over 6,000
          species, ranging across all continents except Antarctica
        </Typography>
      </CardContent>
      <CardActions>
        <Button size="small">Share</Button>
        <Button size="small">Learn More</Button>
      </CardActions>
    </Card>
}

function App() {
  return (
    <React.Fragment>
      <CssBaseline />
      <Container fixed sx={{padding : "10px"}}>
        <Box sx={{ bgcolor: '#cfe8fc', height: '50px', margin: '10px' }} />
          <Box sx={{ bgcolor: '#cfe8fc', height: '50px', margin: '10px' }} />

          <Grid container spacing={2}>
              <Grid item xs={3}>
                <Item>xs=8</Item>
              </Grid>
              <Grid item xs={3}>
                <Item>xs=4</Item>
              </Grid>
              <Grid item xs={3}>
                <Item>xs=4</Item>
              </Grid>
              <Grid item xs={3}>
                <Item>xs=8</Item>
              </Grid>
              <Grid item xs={3}>
                <Item>xs=8</Item>
              </Grid>
        </Grid>
      </Container>
        <Container fixed>
        <Box sx={{ bgcolor: '#ba28fc', height: '50px',  margin: '10px'  }} />
          <Box sx={{ bgcolor: '#ba28fc', height: '50px',  margin: '10px'  }} />
      </Container>
    </React.Fragment>
  );
}

export default App;
