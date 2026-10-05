-- Promote the source title/version to Pandoc metadata and rewrite guide links.
function Link(element)
  element.target = element.target:gsub("SEESTAR_TOOLKIT_USER_GUIDE%.md$",
    "SEESTAR_TOOLKIT_USER_GUIDE.pdf")
  element.target = element.target:gsub("SEESTAR_TOOLKIT_QUICK_START%.md$",
    "SEESTAR_TOOLKIT_QUICK_START.pdf")
  return element
end

function RawInline(element)
  if element.format == "html" and element.text:lower():match("^</?br%s*/?>$") then
    return pandoc.LineBreak()
  end
  return element
end

function Table(element)
  local widths
  if #element.colspecs == 2 then
    widths = {0.36, 0.64}
  elseif #element.colspecs == 3 then
    widths = {0.26, 0.32, 0.42}
  else
    return element
  end
  for index, spec in ipairs(element.colspecs) do
    element.colspecs[index] = {spec[1], widths[index]}
  end
  return element
end

function Pandoc(document)
  local first = document.blocks[1]
  if not first or first.tag ~= "Header" or first.level ~= 1 then
    error("authoritative document must begin with one level-1 title")
  end
  document.meta.title = pandoc.MetaInlines(first.content)

  local version = document.blocks[2]
  if not version or version.tag ~= "Para" or #version.content ~= 1
      or version.content[1].tag ~= "Strong" then
    error("authoritative document must place its strong version line after the title")
  end
  document.meta.subtitle = pandoc.MetaInlines(version.content[1].content)
  document.blocks:remove(1)
  document.blocks:remove(1)
  return document
end
