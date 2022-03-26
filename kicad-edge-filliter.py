import pcbnew
import argparse
import math

def isBoardEdge(edge):
    return isinstance(edge, pcbnew.PCB_SHAPE) and edge.GetLayerName() == "Edge.Cuts"

def findCoincidentPoint(line1, line2):
    # Find the coincident point
    touchingPoint = []
    if (line1.GetStartX() == line2.GetStartX() and line1.GetStartY() == line2.GetStartY()) or \
        (line1.GetStartX() == line2.GetEndX() and line1.GetStartY() == line2.GetEndY()):
        return (line1.GetStartX(), line1.GetStartY())
    elif (line1.GetEndX() == line2.GetStartX() and line1.GetEndY() == line2.GetStartY()) or \
        (line1.GetEndX() == line2.GetEndX() and line1.GetEndY() == line2.GetEndY()):
        return (line1.GetEndX(), line1.GetEndY())
    else:
        return None

def flipLine(line):
    startX = line.GetStartX()
    startY = line.GetStartY()
    line.SetStart(line.GetEnd())
    line.SetEndX(startX)
    line.SetEndY(startY)
    
def shortenLine(line, touchingX, touchingY, radius):
    # Force the touching point to be at the "start" of the line
    if line.GetEndX() == touchingX and line.GetEndY() == touchingY:
        flipLine(line)

    # Ensure our lines touch
    if line.GetStartX() == touchingX and line.GetStartY() == touchingY:
        # Shorten the start of the line
        # We need to reduce the line by radius, in the same direction as the line
        
        if line.GetEndX() == touchingX:
            # Shorten the start, strictly in the Y direction
            if line.GetStartY() > line.GetEndY():
                line.SetStartY(line.GetStartY() - radius)
            else:
                line.SetStartY(line.GetStartY() + radius)
            return (1, line.GetStart())
        elif line.GetEndY() == touchingY:
            # Shorten the start, strictly in the X direction
            if line.GetStartX() > line.GetEndX():
                line.SetStartX(line.GetStartX() - radius)
            else:
                line.SetStartX(line.GetStartX() + radius)
        else:
            print("Oops, haven't implimented this case yet, too much math for this late")
        return (2, line.GetStart())
    else:
        return (0, line.GetStart())

def dot(a, b):
    # Dot product of two wxPoints (treated as vectors)
    return a.x*b.x + a.y*b.y

def mag(point):
    # Magnitude of wxPoint (treated as a vector)
    return math.sqrt(point.x**2 + point.y**2)

def findAngle(a, b):
    # Find the angle between two vectors
    return math.degrees(math.acos(dot(a, b) / mag(a) * mag(b)))

def drawArc(centre, start, end):
    # Draw the shortest arc between start to end, with a given centre
    arc = pcbnew.PCB_SHAPE(board)
    arc.SetShape(pcbnew.S_ARC)
    arc.SetCenter(centre)

    arc.SetStart(start)
    arc.SetEnd(end)

    if findAngle(end - centre, start-centre)*10 != arc.GetArcAngle():
        arc.SetStart(end)
        arc.SetEnd(start)

    arc.SetLayer(pcbnew.Edge_Cuts)
    board.Add(arc)

def addFillet(line1, line2, radius, touchingX, touchingY):
    """
    Shortens two coincident lines, and adds an arc of a given radius between them
    """

    dirn1, start = shortenLine(line1, touchingX, touchingY, radius)
    dirn2, end = shortenLine(line2, touchingX, touchingY, radius)
    
    arcCentre = pcbnew.wxPoint(0, 0)

    if dirn1 == 1 and dirn2 == 2:
        arcCentre.x = line2.GetStartX()
        arcCentre.y = line1.GetStartY()
    elif dirn1 == 2 and dirn2 == 1:
        arcCentre.x = line1.GetStartX()
        arcCentre.y = line2.GetStartY()
    else:
        return False # idk something went wrong

    drawArc(arcCentre, start, end)
    return True

def rectToLines(rect):
    """
    Converts a rectangle to four lines
    """
    return

parser = argparse.ArgumentParser()

parser.add_argument("board", help="Input .kicad_pcb file")
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

# We have several cases to deal with depending on the shape:
#   * Rect - Locate corner points, convert to lines, treat as lines case but you already know the corners
#   * Polygon - Same as Rect, but corners are harder, and determing how to fillet will also be harder (Not supported for now...)
#   * Lines - Find any "pairs" that just touch the ends, add fillet

for i in range(len(edges)):
    for j in range(i+1, len(edges)):
        point = findCoincidentPoint(edges[i], edges[j])
        if point:
            addFillet(edges[i], edges[j], fillet_radius, point[0], point[1])


new_board_name = args.board[:-10] + "_fillet.kicad_pcb"
board.Save(new_board_name)
# board.Save(args.board)
