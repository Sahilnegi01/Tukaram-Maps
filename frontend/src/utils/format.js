export function humanizeAction(value=''){return value.replaceAll('_',' ')}
export function validCoordinates(item){return Number.isFinite(item?.latitude)&&Number.isFinite(item?.longitude)}
