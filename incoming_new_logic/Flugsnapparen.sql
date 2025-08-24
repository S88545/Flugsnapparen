USE [Flugsnapparen]
GO
/****** Object:  Table [dbo].[ApartmentOwnerships]    Script Date: 2025-08-24 10:30:11 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ApartmentOwnerships](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[apartment_id] [int] NOT NULL,
	[member_id] [int] NOT NULL,
	[valid_from] [date] NOT NULL,
	[valid_to] [date] NULL,
	[created_at] [datetime2](7) NOT NULL,
 CONSTRAINT [PK_ApartmentOwnerships] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Apartments]    Script Date: 2025-08-24 10:30:11 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Apartments](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[apartment_number] [nvarchar](5) NOT NULL,
	[sqm_area] [int] NOT NULL,
	[share] [decimal](5, 2) NOT NULL,
	[quarterly_charge] [int] NOT NULL,
	[created_at] [datetime2](7) NOT NULL,
 CONSTRAINT [PK_Apartments] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
 CONSTRAINT [UQ_Apartments_apartment_number] UNIQUE NONCLUSTERED 
(
	[apartment_number] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Members]    Script Date: 2025-08-24 10:30:11 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Members](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[name] [nvarchar](200) NOT NULL,
	[active] [bit] NOT NULL,
	[created_at] [datetime2](7) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
UNIQUE NONCLUSTERED 
(
	[name] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Prognosis]    Script Date: 2025-08-24 10:30:11 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Prognosis](
	[id] [bigint] NOT NULL,
	[year] [bigint] NOT NULL,
	[month] [bigint] NOT NULL,
	[transaction_type_id] [bigint] NOT NULL,
	[prognosis_amount] [decimal](38, 10) NOT NULL,
 CONSTRAINT [PK_dbo__Prognosis] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Suppliers]    Script Date: 2025-08-24 10:30:11 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Suppliers](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[name] [nvarchar](200) NOT NULL,
	[active] [bit] NOT NULL,
	[created_at] [datetime2](7) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
UNIQUE NONCLUSTERED 
(
	[name] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Transactions]    Script Date: 2025-08-24 10:30:11 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Transactions](
	[id] [bigint] NOT NULL,
	[transaction_date] [nvarchar](max) NOT NULL,
	[description] [nvarchar](max) NULL,
	[amount] [decimal](38, 10) NOT NULL,
	[transaction_type_id] [bigint] NOT NULL,
	[supplier_id] [int] NULL,
	[member_id] [int] NULL,
	[supplier] [varchar](255) NULL,
	[member] [varchar](255) NULL,
 CONSTRAINT [PK_dbo__Transactions] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[TransactionTypes]    Script Date: 2025-08-24 10:30:11 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[TransactionTypes](
	[id] [bigint] NOT NULL,
	[name] [nvarchar](max) NOT NULL,
 CONSTRAINT [PK_dbo__TransactionTypes] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[YearlySettings]    Script Date: 2025-08-24 10:30:11 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[YearlySettings](
	[year] [bigint] NOT NULL,
	[total_yta_kvm] [decimal](38, 10) NOT NULL,
	[totala_lan] [decimal](38, 10) NOT NULL,
	[totala_arsavgifter] [decimal](38, 10) NOT NULL,
	[tillgodohavande_placering] [decimal](38, 10) NOT NULL,
 CONSTRAINT [PK_dbo__YearlySettings] PRIMARY KEY CLUSTERED 
(
	[year] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
ALTER TABLE [dbo].[ApartmentOwnerships] ADD  CONSTRAINT [DF_ApartmentOwnerships_created_at]  DEFAULT (sysutcdatetime()) FOR [created_at]
GO
ALTER TABLE [dbo].[Apartments] ADD  CONSTRAINT [DF_Apartments_created_at]  DEFAULT (sysutcdatetime()) FOR [created_at]
GO
ALTER TABLE [dbo].[Members] ADD  DEFAULT ((1)) FOR [active]
GO
ALTER TABLE [dbo].[Members] ADD  DEFAULT (sysutcdatetime()) FOR [created_at]
GO
ALTER TABLE [dbo].[Suppliers] ADD  DEFAULT ((1)) FOR [active]
GO
ALTER TABLE [dbo].[Suppliers] ADD  DEFAULT (sysutcdatetime()) FOR [created_at]
GO
ALTER TABLE [dbo].[ApartmentOwnerships]  WITH CHECK ADD  CONSTRAINT [FK_ApartmentOwnerships_Apartments] FOREIGN KEY([apartment_id])
REFERENCES [dbo].[Apartments] ([id])
GO
ALTER TABLE [dbo].[ApartmentOwnerships] CHECK CONSTRAINT [FK_ApartmentOwnerships_Apartments]
GO
ALTER TABLE [dbo].[ApartmentOwnerships]  WITH CHECK ADD  CONSTRAINT [FK_ApartmentOwnerships_Members] FOREIGN KEY([member_id])
REFERENCES [dbo].[Members] ([id])
GO
ALTER TABLE [dbo].[ApartmentOwnerships] CHECK CONSTRAINT [FK_ApartmentOwnerships_Members]
GO
ALTER TABLE [dbo].[Transactions]  WITH CHECK ADD  CONSTRAINT [FK_Transactions_Members] FOREIGN KEY([member_id])
REFERENCES [dbo].[Members] ([id])
GO
ALTER TABLE [dbo].[Transactions] CHECK CONSTRAINT [FK_Transactions_Members]
GO
ALTER TABLE [dbo].[Transactions]  WITH CHECK ADD  CONSTRAINT [FK_Transactions_Suppliers] FOREIGN KEY([supplier_id])
REFERENCES [dbo].[Suppliers] ([id])
GO
ALTER TABLE [dbo].[Transactions] CHECK CONSTRAINT [FK_Transactions_Suppliers]
GO
ALTER TABLE [dbo].[ApartmentOwnerships]  WITH CHECK ADD  CONSTRAINT [CK_ApartmentOwnerships_dates] CHECK  (([valid_to] IS NULL OR [valid_to]>=[valid_from]))
GO
ALTER TABLE [dbo].[ApartmentOwnerships] CHECK CONSTRAINT [CK_ApartmentOwnerships_dates]
GO
ALTER TABLE [dbo].[Apartments]  WITH CHECK ADD  CONSTRAINT [CK_Apartments_quarterly_charge_nonneg] CHECK  (([quarterly_charge]>=(0)))
GO
ALTER TABLE [dbo].[Apartments] CHECK CONSTRAINT [CK_Apartments_quarterly_charge_nonneg]
GO
ALTER TABLE [dbo].[Apartments]  WITH CHECK ADD  CONSTRAINT [CK_Apartments_share_range] CHECK  (([share]>=(0) AND [share]<=(1)))
GO
ALTER TABLE [dbo].[Apartments] CHECK CONSTRAINT [CK_Apartments_share_range]
GO
ALTER TABLE [dbo].[Apartments]  WITH CHECK ADD  CONSTRAINT [CK_Apartments_sqm_area_pos] CHECK  (([sqm_area]>(0)))
GO
ALTER TABLE [dbo].[Apartments] CHECK CONSTRAINT [CK_Apartments_sqm_area_pos]
GO
