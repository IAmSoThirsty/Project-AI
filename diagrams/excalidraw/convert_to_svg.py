#!/usr/bin/env python3
"""
Excalidraw to SVG Converter

Converts .excalidraw JSON files to SVG format for embedding in documentation.
This is a simplified converter that creates basic SVG representations.
"""

import json
import os
from pathlib import Path
from typing import Any


def convert_excalidraw_to_svg(excalidraw_file: Path, svg_file: Path) -> bool:
    """
    Convert an Excalidraw JSON file to SVG format.
    
    Args:
        excalidraw_file: Path to input .excalidraw file
        svg_file: Path to output .svg file
    
    Returns:
        True if conversion successful, False otherwise
    """
    try:
        with open(excalidraw_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        elements = data.get('elements', [])
        
        # Calculate viewBox dimensions
        min_x, min_y = float('inf'), float('inf')
        max_x, max_y = float('-inf'), float('-inf')
        
        for elem in elements:
            if elem.get('isDeleted', False):
                continue
            x = elem.get('x', 0)
            y = elem.get('y', 0)
            width = elem.get('width', 0)
            height = elem.get('height', 0)
            
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x + width)
            max_y = max(max_y, y + height)
        
        # Add padding
        padding = 50
        viewbox_width = max_x - min_x + (2 * padding)
        viewbox_height = max_y - min_y + (2 * padding)
        
        # Build SVG
        svg_parts = [
            f'<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" ',
            f'viewBox="{min_x - padding} {min_y - padding} {viewbox_width} {viewbox_height}" ',
            f'width="{viewbox_width}" height="{viewbox_height}">',
            f'<style>',
            f'  text {{ font-family: Arial, sans-serif; }}',
            f'  .header {{ font-size: 32px; font-weight: bold; }}',
            f'  .title {{ font-size: 20px; font-weight: bold; }}',
            f'  .body {{ font-size: 14px; }}',
            f'</style>',
        ]
        
        # Convert elements
        for elem in elements:
            if elem.get('isDeleted', False):
                continue
            
            elem_type = elem.get('type', '')
            
            if elem_type == 'rectangle':
                svg_parts.append(_convert_rectangle(elem))
            elif elem_type == 'ellipse':
                svg_parts.append(_convert_ellipse(elem))
            elif elem_type == 'text':
                svg_parts.append(_convert_text(elem))
            elif elem_type == 'arrow':
                svg_parts.append(_convert_arrow(elem))
        
        svg_parts.append('</svg>')
        
        # Write SVG file
        with open(svg_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(svg_parts))
        
        return True
    
    except Exception as e:
        print(f"Error converting {excalidraw_file}: {e}")
        return False


def _convert_rectangle(elem: dict[str, Any]) -> str:
    """Convert rectangle element to SVG rect."""
    x = elem.get('x', 0)
    y = elem.get('y', 0)
    width = elem.get('width', 0)
    height = elem.get('height', 0)
    fill = elem.get('backgroundColor', 'transparent')
    stroke = elem.get('strokeColor', '#000000')
    stroke_width = elem.get('strokeWidth', 1)
    opacity = elem.get('opacity', 100) / 100
    rx = 10 if elem.get('roundness') else 0
    
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" '
        f'opacity="{opacity}" rx="{rx}"/>'
    )


def _convert_ellipse(elem: dict[str, Any]) -> str:
    """Convert ellipse element to SVG ellipse."""
    x = elem.get('x', 0)
    y = elem.get('y', 0)
    width = elem.get('width', 0)
    height = elem.get('height', 0)
    fill = elem.get('backgroundColor', 'transparent')
    stroke = elem.get('strokeColor', '#000000')
    stroke_width = elem.get('strokeWidth', 1)
    opacity = elem.get('opacity', 100) / 100
    
    cx = x + width / 2
    cy = y + height / 2
    rx = width / 2
    ry = height / 2
    
    return (
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" '
        f'opacity="{opacity}"/>'
    )


def _convert_text(elem: dict[str, Any]) -> str:
    """Convert text element to SVG text."""
    x = elem.get('x', 0)
    y = elem.get('y', 0)
    text = elem.get('text', '').replace('<', '&lt;').replace('>', '&gt;')
    font_size = elem.get('fontSize', 14)
    color = elem.get('strokeColor', '#000000')
    
    # Determine CSS class based on font size
    css_class = 'body'
    if font_size >= 32:
        css_class = 'header'
    elif font_size >= 20:
        css_class = 'title'
    
    # Split multiline text
    lines = text.split('\n')
    if len(lines) == 1:
        return (
            f'<text x="{x}" y="{y + font_size}" '
            f'class="{css_class}" fill="{color}" font-size="{font_size}">'
            f'{text}</text>'
        )
    else:
        result = [f'<text x="{x}" y="{y + font_size}" class="{css_class}" fill="{color}" font-size="{font_size}">']
        for i, line in enumerate(lines):
            dy = font_size * 1.2 if i > 0 else 0
            result.append(f'  <tspan x="{x}" dy="{dy}">{line}</tspan>')
        result.append('</text>')
        return '\n'.join(result)


def _convert_arrow(elem: dict[str, Any]) -> str:
    """Convert arrow element to SVG line with arrowhead."""
    x = elem.get('x', 0)
    y = elem.get('y', 0)
    points = elem.get('points', [[0, 0], [0, 0]])
    stroke = elem.get('strokeColor', '#000000')
    stroke_width = elem.get('strokeWidth', 2)
    stroke_style = elem.get('strokeStyle', 'solid')
    
    # Calculate line endpoints
    x1 = x + points[0][0]
    y1 = y + points[0][1]
    x2 = x + points[-1][0]
    y2 = y + points[-1][1]
    
    dash_array = '5,5' if stroke_style == 'dashed' else 'none'
    
    return (
        f'<defs>'
        f'<marker id="arrowhead" markerWidth="10" markerHeight="10" '
        f'refX="5" refY="3" orient="auto">'
        f'<polygon points="0 0, 10 3, 0 6" fill="{stroke}"/>'
        f'</marker>'
        f'</defs>'
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{stroke}" stroke-width="{stroke_width}" '
        f'stroke-dasharray="{dash_array}" marker-end="url(#arrowhead)"/>'
    )


def main() -> None:
    """Main conversion routine."""
    script_dir = Path(__file__).parent
    
    # Find all .excalidraw files
    excalidraw_files = list(script_dir.glob('*.excalidraw'))
    
    if not excalidraw_files:
        print("No .excalidraw files found in current directory")
        return
    
    print(f"Found {len(excalidraw_files)} Excalidraw files to convert")
    
    success_count = 0
    for excalidraw_file in excalidraw_files:
        svg_file = excalidraw_file.with_suffix('.svg')
        print(f"Converting {excalidraw_file.name} → {svg_file.name}...", end=' ')
        
        if convert_excalidraw_to_svg(excalidraw_file, svg_file):
            print("✓")
            success_count += 1
        else:
            print("✗")
    
    print(f"\nConversion complete: {success_count}/{len(excalidraw_files)} successful")


if __name__ == '__main__':
    main()
