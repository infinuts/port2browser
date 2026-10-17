-- Original MIT fixture. One step per press, generated geometry/audio, native filesystem save.
local state = {x=24, collected=0, started=0, sounds=0, saves=0, focused=1}
local tone
local function journal()
  local major, minor, revision = love.getVersion()
  love.filesystem.write('observed.json', string.format('{"x":%d,"collected":%d,"started":%d,"sounds":%d,"saves":%d,"focused":%d,"engine":"%d.%d.%d"}', state.x,state.collected,state.started,state.sounds,state.saves,state.focused,major,minor,revision))
end
function love.load()
  love.filesystem.setIdentity('port2browser-love-beacon')
  if love.filesystem.getInfo('save.txt') then
    local data=love.filesystem.read('save.txt')
    local x,c=data:match('^(%d+) (%d+)$')
    x,c=tonumber(x),tonumber(c)
    if x and c and x>=0 and x<=288 and (c==0 or c==1) then state.x=x;state.collected=c end
  end
  local samples=love.sound.newSoundData(4410,22050,16,1)
  for i=0,4409 do samples:setSample(i, math.sin(i*440*2*math.pi/22050)*0.15) end
  tone=love.audio.newSource(samples,'static')
  journal()
end
function love.keypressed(key, scancode, repeated)
  if repeated then return end
  if key=='return' then state.started=1 end
  if state.started==1 then
    if key=='right' then state.x=math.min(288,state.x+12) end
    if key=='left' then state.x=math.max(0,state.x-12) end
    if key=='space' and math.abs(state.x-120)<=12 and state.collected==0 then
      state.collected=1;state.sounds=state.sounds+1;tone:stop();tone:play()
    end
    if key=='s' then
      assert(love.filesystem.write('save.txt',state.x..' '..state.collected))
      state.saves=state.saves+1
    end
  end
  journal()
end
function love.focus(focused) state.focused=focused and 1 or 0;journal() end
function love.draw()
  love.graphics.clear(15/255,23/255,42/255)
  love.graphics.setColor(state.collected==1 and 30/255 or 1,state.collected==1 and 180/255 or 190/255,60/255)
  love.graphics.rectangle('fill',240,128,48,48)
  love.graphics.setColor(56/255,189/255,248/255)
  love.graphics.rectangle('fill',state.x*2,200,48,48)
  love.graphics.setColor(1,1,1)
  love.graphics.print('LOVE Beacon | x='..state.x..' | collected='..state.collected..' | saves='..state.saves,16,20)
  love.graphics.print('Enter: start  Arrows: move  Space: collect  S: save',16,330)
end
