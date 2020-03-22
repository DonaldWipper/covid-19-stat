 function restore_colors() {
     for (i = 0; i < visualDonatData.length; i++) {
         d3.select("#ArcEllipse" + i).style("fill", visualDonatData[i]["color"]);
     }
 }

 function restore_colors_outArcs() {
     for (i = 0; i < outArcsData.length; i++) {
         d3.select("#outArc" + i).style("fill", outArcsData[i]["color"]);
     }
 }

 function setClicked(Array) {
     for (i = 0; i < Array.length; i++) {
         d3.select("#ArcEllipse" + Array[i]).style("fill", "#debcd1");
     }
 }



//дял каждой части находим первый и последний кусочек     
function getPartBounces(visualDonatData, part_bounces) {
    for (i = 0; i < visualDonatData.length; i++) {
        cur_group = visualDonatData[i]["id_group"];
        if (cur_group == -1) {
            continue;
        }
        cur_group_left = part_bounces[cur_group][0]
        cur_group_right = part_bounces[cur_group][1]
        
        if (i < cur_group_left) {
            part_bounces[cur_group][0] = i
        }
        if (i > cur_group_right) {
            part_bounces[cur_group][1] = i
        }
    }
}


 //рисуем эллипс 
 function createDonatDiagram(
     visualDonatData,
     pie,
     arc,
     global_arc_koefX, //коэффициенты растяжения круга
     global_arc_koefY,
     outerRadius,
     fontSizeInnerSlice,                           
     nameElement = "visualDonatArcs", // имя основного элемента
     ArcElement = "visualDonatArc", // каркас для текстовых элементов
     textArcElement = "visualDonatText",
     font_family = "dusha"
) // текст, который наносится на каркас
 {
    var part_bounces = {
        "0": [10000, -1],
        "1": [10000, -1],
        "2": [10000, -1],
        "3": [10000, -1]
    }
    
    //параметр, который задает каждую арку
    var arcOut = {
        firstLoc: "",
        radLoc: "",
        secLoc: "",
        firstSmallLoc: "",
        secSmallLoc: "",
        radSmallLoc: ""
    }
           

    getPartBounces(visualDonatData, part_bounces);
    svg.selectAll("." + nameElement)
         .data(pie(visualDonatData))
         .enter().append("path")
         .attr("class", nameElement)
         .attr("d", arc)
         .attr("id", nameElement)
         .style("fill", function(d, i) {
             return "none";
         })
         .each(function(d, i) {
             var firstDotOuterEx = /M(.*?)A/;
             var radOuterEx = /A(.*?)0 0,1/;
             var secondDotOuterEx = /0 0,1(.*?)L/;
             var firstInnerDotEx = /L(.*?)A/;
             var radSmallElEx = /A(.*?)0 0,0/
             var secondSmallDotEx = /0 0,0(.*?)Z/;

       
             
             firstLoc = firstDotOuterEx.exec(d3.select(this).attr("d"))[1]
             radLoc = radOuterEx.exec(d3.select(this).attr("d"))[1]

             secLoc = secondDotOuterEx.exec(d3.select(this).attr("d"))[1]
             firstSmallLoc = firstInnerDotEx.exec(d3.select(this).attr("d"))[1]

             secSmallLoc = secondSmallDotEx.exec(d3.select(this).attr("d"))[1]
             radSmallLoc = radSmallElEx.exec(d3.select(this).attr("d"))[1]
             radSmallLoc = radSmallElEx.exec(radSmallLoc + "0 0,0")[1]
             
            
             var first = firstLoc.split(",");
             var second = secLoc.split(",");
             var rad = radLoc.split(",")

             //точки и радиус для внутренней арки
             newFirst = getEllipseCoords(parseFloat(first[0]), parseFloat(first[1]), ellipse_koefX, ellipse_koefY, outerRadius).join(",")
             newLast = getEllipseCoords(parseFloat(second[0]), parseFloat(second[1]), ellipse_koefX, ellipse_koefY, outerRadius).join(",")
             newRad = [rad[0] * ellipse_koefX, rad[1] * ellipse_koefY].join(",")

             //точки для внешней арки
             newFirstOut = getEllipseCoords(parseFloat(first[0]), parseFloat(first[1]), global_arc_koefX, global_arc_koefY, outerRadius).join(",")
             newSecOut = getEllipseCoords(parseFloat(second[0]), parseFloat(second[1]), global_arc_koefX, global_arc_koefY, outerRadius).join(",")


             FirstPath = "M" + newFirst + "A" + newRad + " 0 0, 1" + newLast
             ellipseInnerArc = FirstPath + "L" + firstSmallLoc + "A" + radSmallLoc + "0 0,0" + secSmallLoc + "Z"
        
            
             
             console.log("ellipseInnerArc " + ellipseInnerArc)
             image_width = getDistance(firstSmallLoc.split(","), secSmallLoc.split(","))
             path_length_no_image = getDistance(secSmallLoc.split(","), newFirst.split(","))
           
             res = image_width / path_length_no_image > 0.4
             //cделаем картинку масшатбируемой
             while ((res == true) && (image_width > 1)) {
                 image_width -= 0.1
                 res = image_width / path_length_no_image > 0.4
             }
                 
             //центры долек, чтобы писать в центре
             centreSec = getPointDivided(newLast.split(","), newFirst.split(",")).join(",")
             centreFirst = getPointDivided(firstSmallLoc.split(","), secSmallLoc.split(",")).join(",")
        
             centre_path_length = getDistance(centreFirst.split(","), centreSec.split(","))
            
        
             k = image_width * 1.0 / (centre_path_length - image_width) //коэффицент пути
             nextPointCentre = getPointDivided(centreFirst.split(","), centreSec.split(","), k).join(",")

             k2  = image_width * 1.0 / (path_length_no_image - image_width) 
             nextPointToImage = getPointDivided(newFirst.split(","), secSmallLoc.split(","), 1/k2).join(",")
        
             if (visualDonatData[i]["id_group"] != 0) { //разные направления пути для разных видов долек
                 textArc = "M" + newLast + "L" + firstSmallLoc + "Z"
                 textArcCentre = "M " + centreFirst + " L" + centreSec
             } else {
                 //textArc = "M" + secSmallLoc + "L" + newFirst + "Z"
                 textArc = "M" + newFirst + "L" +  nextPointToImage  + "Z"
                 textArcCentre = "M" + centreSec + "L" + nextPointCentre + "Z"
             }


             newRadOut = [global_arc_koefX * rad[0], global_arc_koefY * rad[1]].join(",")

             size_sec = getDistance(centreSec.split(","), centreFirst.split(",")) //size of sector
             angle = getRotateAngle(firstSmallLoc.split(","), secSmallLoc.split(",")) //угол поворота для смещения картинки

             //если текущий кусок самый крайний в группе
             cur_group = visualDonatData[i]["id_group"]
             if (cur_group != -1) {
                 if (part_bounces[cur_group][0] == i) {
                     var a = Object.assign({}, arcOut)
                     a["firstLoc"] = newFirstOut
                     a["radLoc"] = newRadOut
                     a["firstSmallLoc"] = newFirst
                     a["radSmallLoc"] = newRad
                     out_arcs.push(a)
                 }
                 if (part_bounces[cur_group][1] == i) {
                     out_arcs[cur_group]["secLoc"] = newSecOut
                     out_arcs[cur_group]["secSmallLoc"] = newLast
                 }
             }

             svg.append("path")
                 .attr("class", "hidden" + ArcElement)
                 .attr("id", ArcElement + i)
                 .attr("d", textArc)
                 .style("fill", visualDonatData[i]["color"]);

             //Маленькие внутренние дольки

             svg.append("path")
                 .attr("class", "slice_ellipse")
                 .attr("id", "ArcEllipse" + i)
                 .attr("stroke-width", 2)
                 .attr("stroke", function() { 
                     if (visualDonatData[i]["id_group"] != -1)  {
                         return "black";
                     } else {
                        return "none"; 
                     }
                 })
                 .attr("d", ellipseInnerArc)
                 .style("fill", visualDonatData[i]["color"])
                 .on("mouseover", function() {
                     restore_colors()
                     d3.select(this).style("fill", "#debcd1");
                     setClicked(click_events[i]);

                 })
                 .on("mouseout", function(d, i) {
                     restore_colors()
                         //d3.select(this).style("fill", visualDonatData[i]["color"]);
                 });

             svg.append("path")
                 .attr("class", "hidden" + ArcElement + "Centre")
                 .attr("id", ArcElement + "Centre" + i)
                 .attr("d", textArcCentre)
                 .style("fill", "none");

             svg.append("image")
                 .attr("width",
                     image_width)
                 .attr("height", image_width)
                 .attr("x", firstSmallLoc.split(",")[0])
                 .attr("y", firstSmallLoc.split(",")[1])
                 .attr("id", "rect" + i)
                 .attr("transform", function() {
                     a = 180 + angle
                     if (visualDonatData[i]["id_group"] == 0) {
                         //a = angle 
                         return "rotate(" + a + ", " + firstSmallLoc.split(",")[0] + " ," + firstSmallLoc.split(",")[1] + ")" +
                               "translate(-" + image_width + ",0)"
                     } else {
                         return ""
                     }

                 })
                 .attr("xlink:href", function() {
                     //console.log("")
                     if (visualDonatData[i]["id_group"] == 0) {
                         return visualDonatData[i]["image"]
                     }
                 });
             //Append the label names on the outside


         });

     //текста добавляем отдельно. Это все, что в центре         
     svg.selectAll("." + textArcElement + "Centre")
         .data(pie(visualDonatData))
         .enter().append("text")
         .style("font-size", fontSizeInnerSlice / 1.2 + "px")
         .style("font-family", font_family)
         .style("fill", "#ffffff")
         .attr("class", ArcElement + "Centre")
         .attr("pointer-events", "none")
         .append("textPath")
         .attr("href", function(d, i) {
             return "#" + ArcElement + "Centre" + i;
         })
         .attr("startOffset", function(d, i) {
             if (d.data.id_group == 0) {
                 return "47%";
             } else {
                 return "0%";
             }
         })
         .attr("text-anchor", function(d, i) {
             if (d.data.id_group == 0) {
                 return "end";
             } else {
                 return "start";
             }
         })
         //.attr("xlink:href",function(d) {return d.data.image;})
         .text(function(d, i) {
             if (d.data.id_group == 2) {
                 return d.data.name.split(";")[1].toUpperCase();
             } else {
                 return "";
                 
             }
         })

     //текст внизу ячеек
     svg.selectAll("." + textArcElement)
         .data(pie(visualDonatData))
         .enter().append("text")
         .style("font-size", function(d, i) {
             if (d.data.id_group == 2) {
                 return fontSizeInnerSlice / 1.4 + "px";
             } else {
                 return fontSizeInnerSlice;
             }
         })


     .style("font-family", font_family)
         .attr("class", textArcElement)
         .attr("pointer-events", "none")
         .append("textPath")
         .attr("href", function(d, i) {
             return "#" + ArcElement + i;
         })
         .attr("startOffset", function(d, i) {
             if (d.data.id_group == 0) {
                 return "50%";
             } else {
                 return "50%";
             }
         })
         .attr("text-anchor", function(d, i) {
             if (d.data.id_group == 0) {
                 return "end";
             } else {
                 return "start";
             }
         })
        
         //.attr("xlink:href",function(d) {return d.data.image;})
         .text(function(d, i) {
             if (d.data.id_group == 2) {
                 return d.data.name.split(";")[0];
             } else {
                 return d.data.name;
             }
         })
        .each(function (d, i) {
            var self = d3.select(this),
            pathLen = d3.select("#" + ArcElement + i).node().getTotalLength();
            res = this.getComputedTextLength() > pathLen  / 2.3
            font_size = parseFloat(d3.select(this).style("font-size").replace('px', ''))
            while ((res == true) && (font_size > 1)) {
                console.log('text more length', d.data.name, this.getComputedTextLength(), pathLen / 2.3)
                console.log(font_size)
                font_size -=  1
                d3.select(this).style("font-size", font_size + "px")  
                res = this.getComputedTextLength() > pathLen / 2.3
                console.log(font_size)
                
                
            }
            

         })
     
         
 }