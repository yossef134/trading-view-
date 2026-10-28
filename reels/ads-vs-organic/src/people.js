    // flat sticker people (white cut-out edge + soft shadow, after the collage stickers in the references)
    // spec: g = "m" man | "h" woman in hijab | "f" woman; skin, hair, top, scarf; beard, stache, glasses
    const PERSON_EDGE = '<filter id="ppl-edge-ID" x="-12%" y="-12%" width="124%" height="124%"><feMorphology in="SourceAlpha" operator="dilate" radius="7" result="d"/><feFlood flood-color="#ffffff"/><feComposite in2="d" operator="in" result="e"/><feMerge><feMergeNode in="e"/><feMergeNode in="SourceGraphic"/></feMerge></filter>';
    const person = (p, uid) => {
      const ink = "#13213F", S = p.skin, H = p.hair || "#2B2118";
      const face = (cy) =>
        `<path d="M74 ${cy - 16} q9 -6 18 0 M108 ${cy - 16} q9 -6 18 0" stroke="${p.g === "h" ? ink : H}" stroke-width="4.5" fill="none" stroke-linecap="round"/>` +
        `<circle cx="83" cy="${cy}" r="5.5" fill="${ink}"/><circle cx="117" cy="${cy}" r="5.5" fill="${ink}"/>` +
        `<circle cx="70" cy="${cy + 16}" r="8" fill="#F28C6B" opacity=".25"/><circle cx="130" cy="${cy + 16}" r="8" fill="#F28C6B" opacity=".25"/>` +
        (p.glasses ? `<g fill="none" stroke="${ink}" stroke-width="4"><circle cx="83" cy="${cy}" r="15"/><circle cx="117" cy="${cy}" r="15"/><path d="M98 ${cy} h4"/></g>` : "") +
        (p.beard ? `<path d="M57 ${cy + 2} C58 ${cy + 46} 78 ${cy + 58} 100 ${cy + 58} C122 ${cy + 58} 142 ${cy + 46} 143 ${cy + 2} C138 ${cy + 24} 128 ${cy + 32} 118 ${cy + 26} C110 ${cy + 22} 90 ${cy + 22} 82 ${cy + 26} C72 ${cy + 32} 62 ${cy + 24} 57 ${cy + 2} Z" fill="${H}"/>` : "") +
        (p.stache || p.beard ? `<path d="M83 ${cy + 25} C91 ${cy + 18} 109 ${cy + 18} 117 ${cy + 25} C108 ${cy + 28} 92 ${cy + 28} 83 ${cy + 25} Z" fill="${H}"/>` : "") +
        `<path d="M89 ${cy + 31} Q100 ${cy + 40} 111 ${cy + 31}" stroke="${p.beard ? "#ffffff" : ink}" stroke-width="4.5" fill="none" stroke-linecap="round"/>`;
      let g = `<path d="M12 252 C12 198 46 172 100 172 C154 172 188 198 188 252 Z" fill="${p.top}"/>`;
      if (p.g === "h") {
        g += `<path d="M100 40 C58 40 42 76 44 114 C45 148 54 170 64 184 C40 192 22 210 18 252 L182 252 C178 210 160 192 136 184 C146 170 155 148 156 114 C158 76 142 40 100 40 Z" fill="${p.scarf}"/>`;
        g += `<path d="M64 184 C82 200 118 200 136 184" stroke="${ink}" stroke-opacity=".18" stroke-width="5" fill="none"/>`;
        g += `<ellipse cx="100" cy="114" rx="37" ry="45" fill="${S}"/>` + face(108);
      } else {
        g += `<path d="M84 146 L116 146 L116 182 C110 192 90 192 84 182 Z" fill="${S}"/><path d="M84 160 L116 160 L116 170 C108 176 92 176 84 170 Z" fill="${ink}" opacity=".12"/>`;
        if (p.g === "f") g += `<path d="M50 112 C46 62 72 42 100 42 C130 42 154 62 150 112 C152 150 148 180 142 196 L58 196 C52 180 48 150 50 112 Z" fill="${H}"/>`;
        else g += `<path d="M84 176 L100 204 L116 176" fill="none" stroke="#ffffff" stroke-opacity=".7" stroke-width="6" stroke-linejoin="round"/>`;
        g += `<circle cx="56" cy="110" r="10" fill="${S}"/><circle cx="144" cy="110" r="10" fill="${S}"/>`;
        g += `<ellipse cx="100" cy="106" rx="44" ry="52" fill="${S}"/>`;
        g += p.g === "f"
          ? `<path d="M56 100 C58 62 82 52 102 54 C126 56 142 70 144 100 C132 84 114 76 98 78 C80 82 66 90 56 100 Z" fill="${H}"/>`
          : `<path d="M56 104 C52 62 74 44 100 44 C128 44 150 62 144 104 C140 86 132 76 118 72 C102 80 78 78 62 84 C58 90 57 96 56 104 Z" fill="${H}"/>`;
        g += face(104);
      }
      return `<svg class="ppl" viewBox="-10 -10 220 272"><defs>${PERSON_EDGE.replace("ID", uid)}</defs><g filter="url(#ppl-edge-${uid})">${g}</g></svg>`;
    };
    const SKIN = ["#F2C7A5", "#E3AE88", "#C98F66", "#9C6644"];
    const PEOPLE = [
      { g: "h", skin: SKIN[1], scarf: "#2D4A7A", top: "#2D4A7A" },
      { g: "m", skin: SKIN[2], hair: "#2B2118", top: "#13213F", beard: true },
      { g: "h", skin: SKIN[0], scarf: "#C9D2E3", top: "#7D8597" },
      { g: "m", skin: SKIN[1], hair: "#1E1A17", top: "#C9D2E3", glasses: true },
      { g: "f", skin: SKIN[0], hair: "#4A3426", top: "#13213F" },
      { g: "m", skin: SKIN[3], hair: "#1E1A17", top: "#7D8597", stache: true },
      { g: "h", skin: SKIN[2], scarf: "#13213F", top: "#C9D2E3" },
      { g: "m", skin: SKIN[0], hair: "#8A8F99", top: "#2D4A7A", glasses: true, stache: true },
      { g: "h", skin: SKIN[1], scarf: "#FFD9C2", top: "#13213F" },
      { g: "m", skin: SKIN[1], hair: "#2B2118", top: "#DCE1EA" },
      { g: "h", skin: SKIN[3], scarf: "#7D8597", top: "#2D4A7A" },
      { g: "m", skin: SKIN[2], hair: "#2B2118", top: "#2D4A7A", beard: true, glasses: true },
      { g: "f", skin: SKIN[2], hair: "#1E1A17", top: "#C9D2E3" },
    ];
