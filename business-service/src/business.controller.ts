import { Body, Controller, Get, Post } from '@nestjs/common';
import { IsString } from 'class-validator';

class CreateCustomerDto {
  @IsString()
  name!: string;
}

class CreateTemplateDto {
  @IsString()
  templateId!: string;

  @IsString()
  templateName!: string;
}

@Controller()
export class BusinessController {
  @Get('customers')
  customers() {
    return [{ id: 'customer_001', name: 'Sample Customer' }];
  }

  @Post('customers')
  createCustomer(@Body() body: CreateCustomerDto) {
    return {
      id: 'customer_002',
      name: body.name,
      createdAt: new Date().toISOString()
    };
  }

  @Get('templates')
  templates() {
    return [
      {
        templateId: 'tpl_001',
        templateName: 'Classic Shirt',
        status: 'active'
      }
    ];
  }

  @Post('templates')
  createTemplate(@Body() body: CreateTemplateDto) {
    return {
      templateId: body.templateId,
      templateName: body.templateName,
      stored: true
    };
  }

  @Get('fabrics')
  fabrics() {
    return [{ id: 'fabric_001', name: 'Cotton Poplin', color: 'Blue' }];
  }

  @Get('orders')
  orders() {
    return [{ id: 'order_001', status: 'draft' }];
  }

  @Get('audit-logs')
  auditLogs() {
    return [{ id: 'audit_001', event: 'business_service_started' }];
  }
}

