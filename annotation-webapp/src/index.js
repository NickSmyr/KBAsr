import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import Annotate from "./Annotate";

// ReactDOM.render(
//   <React.StrictMode>
//     <App />
//   </React.StrictMode>,
//   document.getElementById('root')
// );

function onSubmit(str){
    alert("Received response: " + str)
}

ReactDOM.render(
  <React.StrictMode>
    <Annotate blocks={
            [
                ["nya stället", "vi gör så rätt"],
                ["mats", "mats"],
                ["eller", "håller"],
                ["ordning", "ordning"],
                ["nya stället", "vi gör så rätt vi gör så rätt vi gör så rätt vi gör så rätt vi gör så rätt"],
                ["eller", "håller"],
                ["ordning", "ordning"],
                ["nya stället", "vi gör så rätt vi gör så rätt vi gör så rätt vi gör så rätt vi gör så rätt"],
                ["eller", "håller"],
                ["ordning", "ordning"],
                ["nya stället", "vi gör så rätt vi gör så rätt vi gör så rätt vi gör så rätt vi gör så rätt"],
                ["eller", "håller"],
                ["ordning", "ordning"],
                ["nya stället", "vi gör så rätt vi gör så rätt vi gör så rätt vi gör så rätt vi gör så rätt"],
            ]
        }
              onSubmit={onSubmit}
              blockEndTimes={[
                  1,2,3,4,5,6,7,8,9,10,11,12,13,14
              ]}
    />
  </React.StrictMode>,
  document.getElementById('root')
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals(console.log);
