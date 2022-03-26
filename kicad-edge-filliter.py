import pcbnew
import argparse
import math

def isBoardEdge(edge):
    return isinstance(edge, pcbnew.PCB_SHAPE) and edge.GetLayerName() == "Edge.Cuts"

def findCoincidentPoint(line1, line2):
    # Find the coincident point
    if (line1.GetStartX() == line2.GetStartX() and line1.GetStartY() == line2.GetStartY()) or \
        (line1.GetStartX() == line2.GetEndX() and line1.GetStartY() == line2.GetEndY()):
        return pcbnew.wxPoint(line1.GetStartX(), line1.GetStartY())
    elif (line1.GetEndX() == line2.GetStartX() and line1.GetEndY() == line2.GetStartY()) or \
        (line1.GetEndX() == line2.GetEndX() and line1.GetEndY() == line2.GetEndY()):
        return pcbnew.wxPoint(line1.GetEndX(), line1.GetEndY())
    else:
        return None

def flipLine(line):
    startX = line.GetStartX()
    startY = line.GetStartY()
    line.SetStart(line.GetEnd())
    line.SetEnd(pcbnew.wxPoint(startX, startY))

def shortenLine(line, touchingPoint, distance):
    # Force the touching point to be at the "end" of the line
    if line.GetStart() == touchingPoint:
        flipLine(line)

    # Check we're actually at the end
    if line.GetEnd() == touchingPoint:
        # We need to reduce the line by distance, in the same direction as the line
        dirn = norm_vector(line.GetEnd() - line.GetStart(), length=distance)
        line.SetEnd(line.GetEnd() - dirn)

        return (dirn, line.GetEnd())
    return (None, None)

def dot(a, b):
    # Dot product of two wxPoints (treated as vectors)
    return a.x*b.x + a.y*b.y

def mag(point):
    # Magnitude of wxPoint (treated as a vector)
    return math.sqrt(point.x**2 + point.y**2)

def det(a, b):
    # Determinant of wxPoint (treasted as a vector)
    return (a.x * b.y) - (a.y * b.x)

def norm_vector(point, length=1):
    # Return a new normalised wxPoint (treated as a vector)
    # Can optionally multiply by a const
    return pcbnew.wxPoint(length * point.x / mag(point), length * point.y / mag(point))

def findAngle(a, b):
    # Find the angle between two vectors
    return math.degrees(math.acos(dot(a, b) / (mag(a) * mag(b))))

def findAngleSigned(a, b):
    return math.degrees(math.atan2(det(a, b), dot(a, b)))

def sign(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0

def drawArc(centre, start, end):
    """
    Draw the shortest arc between start to end, with a given centre
    """
    arc = pcbnew.PCB_SHAPE(board)
    arc.SetShape(pcbnew.S_ARC)
    arc.SetLayer(pcbnew.Edge_Cuts)
    arc.SetCenter(centre)
    arc.SetStart(start)
    arc.SetEnd(end)

    # Flip the start and end if the arc produced isn't the shortest possible
    if round(findAngle(end - centre, start-centre)*10, 2) != round(arc.GetArcAngle(), 2):
        arc.SetStart(end)
        arc.SetEnd(start)

    board.Add(arc)

def addFillet(line1, line2, radius, touchingPoint):
    """
    Shortens two coincident lines, and adds an arc of a given radius between them
    """

    # Ensure the ends are at the touching point for consistency
    if line1.GetStart() == touchingPoint:
        flipLine(line1)
    if line2.GetStart() == touchingPoint:
        flipLine(line2)

    # Calculate distance required to shorten each line by given the radius of the fillet
    angle = findAngle(line1.GetStart() - touchingPoint, line2.GetStart() - touchingPoint)
    distance = radius / math.tan(math.radians(angle / 2))

    # Shorten the lines, getting the direction as a vector that the line was reduced in
    dirn1, start = shortenLine(line1, touchingPoint, distance)
    dirn2, end = shortenLine(line2, touchingPoint, distance)

    # Now we calculate the centre of the arc
    # We will use the direction the (start) line was reduced in, rotate it 90deg towards the other line, scale it by the radius, and then add to the start
    dirn1 = norm_vector(dirn1, length=radius)
    # Find the direction we need to rotate
    rotDirn = sign(findAngleSigned(dirn1, dirn2))
    
    # Rotate 90 degrees, towards the end
    dirn1Rot = pcbnew.wxPoint(rotDirn*dirn1.y, -1*rotDirn*dirn1.x)

    arcCentre = start + dirn1Rot

    drawArc(arcCentre, start, end)

def rectToLines(rect):
    """
    Converts a rectangle to four lines
    """
    return

parser = argparse.ArgumentParser()

parser.add_argument("board", help="Input .kicad_pcb file")
parser.add_argument("-o", "--output", help="Output .kicad_pcb file. Will overwrite the input file if not specified")
parser.add_argument("-r", "--radius", help="Radius of the corner edge", default=2.0, type=float)

args = parser.parse_args()

fillet_radius = int(args.radius * 1000000)

board = pcbnew.LoadBoard(args.board)

edges = []
for drawing in board.GetDrawings():
    if isBoardEdge(drawing):

        if drawing.ShowShape() == "Rect":
            # Convert a rectangle into a bunch of lines and add them to the list of edges
            pass
        elif drawing.ShowShape() == "Polygon":
            # Convert polygon to a bunch of lines and add them to the list of edges
            pass
        elif drawing.ShowShape() == "Line":
            edges.append(drawing)

for i in range(len(edges)):
    for j in range(i+1, len(edges)):
        point = findCoincidentPoint(edges[i], edges[j])
        if point:
            addFillet(edges[i], edges[j], fillet_radius, point)

if (args.output):
    board.Save(args.output)
else:
    board.Save(args.board)

