//
// Copyright (c) 2015 by Antonio Molina Garcia-Retamero. All Rights Reserved.
//

function onLinkOver(sender){
  console.log("Get over " + $(sender).data("fname"));
  var swu = getFunDoc($(sender).data("fname"));
  if(swu == null)
    console.log("No lo ha encontrado");
  else
    console.log(swu.reducedHTMLFile);
}

function getFunDoc(name){
  for (var i = 0; i < shortLibrary.length; i++) {
    console.log(shortLibrary[i] );
    if (shortLibrary[i].rdef === name)
      return shortLibrary[i];
  }
}
// Capturo el evento del raton para mostrar el pop up
