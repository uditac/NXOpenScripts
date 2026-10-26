# NX Open Python journal: inner surface area of a pipe
# Run in NX: File > Execute > NX Open... (or Alt+F8) and pick this file.
import math
import NXOpen
import NXOpen.UF


def main():
    session = NXOpen.Session.GetSession()
    uf = NXOpen.UF.UFSession.GetUFSession()
    part = session.Parts.Work
    lw = session.ListingWindow
    lw.Open()

    # 1) Collect all cylindrical faces of all solid bodies
    cyl = []  # (face, radius, body)
    for body in part.Bodies:
        if not body.IsSolidBody:
            continue
        for face in body.GetFaces():
            if face.SolidFaceType == NXOpen.Face.FaceType.Cylindrical:
                # AskFaceData -> (type, point, dir, box, radius, rad_data, norm_dir)
                data = uf.Modl.AskFaceData(face.Tag)
                radius = data[4]
                cyl.append((face, radius, body))

    if not cyl:
        lw.WriteLine("No cylindrical faces found.")
        return

    # 2) For a pipe, the inner surface = the cylindrical faces with the smallest radius
    r_min = min(r for _, r, _ in cyl)
    tol = 1e-4
    inner = [(f, r, b) for f, r, b in cyl if abs(r - r_min) < tol]

    # 3) Measure area (units follow the part: mm here)
    unit_area = part.UnitCollection.FindObject("SquareMilliMeter")
    unit_len = part.UnitCollection.FindObject("MilliMeter")

    total = 0.0
    lw.WriteLine("Inner radius: %.4f mm  (ID = %.4f mm)" % (r_min, 2 * r_min))
    for i, (face, r, body) in enumerate(inner, 1):
        mf = part.MeasureManager.NewFaceProperties(unit_area, unit_len, 0.99, [face])
        area = mf.Area
        total += area
        lw.WriteLine("  Face %d: %.4f mm^2" % (i, area))
        mf.Dispose()

    lw.WriteLine("TOTAL INNER SURFACE AREA = %.4f mm^2" % total)
    lw.WriteLine("                         = %.6f m^2" % (total / 1e6))


if __name__ == "__main__":
    main()