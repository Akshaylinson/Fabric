import { Controller, Get } from '@nestjs/common';

@Controller('v1')
export class ProxyController {
  @Get('status')
  status() {
    return {
      service: 'gateway',
      routes: ['auth', 'business', 'orchestrator'],
      message: 'Gateway scaffold is ready for routing and auth middleware'
    };
  }
}

