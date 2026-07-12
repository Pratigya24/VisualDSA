import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ProgressRing } from "@/shared/components/progress-ring";

describe("ProgressRing", () => {
  it("renders a full ring with zero dash-offset at progress=1", () => {
    const { container } = render(<ProgressRing progress={1} size={40} strokeWidth={4} />);
    const circles = container.querySelectorAll("circle");
    const progressCircle = circles[1];
    expect(progressCircle).toBeDefined();
    expect(progressCircle?.getAttribute("stroke-dashoffset")).toBe("0");
  });

  it("clamps out-of-range progress values into [0, 1]", () => {
    const { container: over } = render(<ProgressRing progress={2} size={40} strokeWidth={4} />);
    const { container: under } = render(<ProgressRing progress={-1} size={40} strokeWidth={4} />);

    const overOffset = over.querySelectorAll("circle")[1]?.getAttribute("stroke-dashoffset");
    const underOffset = under.querySelectorAll("circle")[1]?.getAttribute("stroke-dashoffset");

    expect(overOffset).toBe("0");
    expect(Number(underOffset)).toBeCloseTo(2 * Math.PI * ((40 - 4) / 2));
  });
});
