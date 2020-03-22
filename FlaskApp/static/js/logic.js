function getEllipseCoords(coorX, coorY, koefX, koefY, radius) {
    newX = radius * koefY * coorX * koefX / Math.sqrt(koefY * koefY * coorX * coorX + coorY * coorY * koefX * koefX);
    newY = newX * coorY / coorX;
    return [newX, newY]
}
         
function getPointDivided(point1, point2, k = 1.0) {
   x = (parseFloat(point1[0]) + k * parseFloat(point2[0])) / (k + 1)
   y = (parseFloat(point1[1]) + k * parseFloat(point2[1])) / (k + 1)
   return [x, y]
}

function getDistance(point1, point2) {
    return Math.sqrt(Math.pow(parseFloat(point1[0]) - parseFloat(point2[0]), 2) +  
                     Math.pow(parseFloat(point1[1]) - parseFloat(point2[1]), 2) )
}

//угол наклона вектора относительно оси  OY
function getRotateAngle(point1, point2) {
    dist = getDistance(point1, point2)
    //угол(a, b) = arccos((a * b) / (|a| * |b|))
    vect1 = [point2[0] - point1[0], point2[1] - point1[1]]                
    vect2 = [0, - 1]
    mult = vect1[0] * vect2[0] + vect1[1] * vect2[1]
    d = mult / dist
    if (vect1[0] > 0) {
        return Math.acos(d) / Math.PI * 180
    } else {
        return -Math.acos(d) / Math.PI * 180    
    }

}

